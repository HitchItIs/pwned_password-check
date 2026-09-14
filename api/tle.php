<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

$cacheDir = dirname(__DIR__) . '/cache';
if (!is_dir($cacheDir)) {
    @mkdir($cacheDir, 0775, true);
}

$ttlSeconds = 6 * 60 * 60;
$group = strtolower(trim((string)($_GET['group'] ?? 'stations')));

$endpointMap = [
    'stations' => 'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle',
    'starlink' => 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle',
    'debris' => 'https://celestrak.org/NORAD/elements/gp.php?GROUP=1999-025&FORMAT=tle',
    '1999-025' => 'https://celestrak.org/NORAD/elements/gp.php?GROUP=1999-025&FORMAT=tle',
];

if (!isset($endpointMap[$group])) {
    http_response_code(400);
    echo json_encode(['error' => 'Unsupported group'], JSON_PRETTY_PRINT);
    exit;
}

$cacheKey = preg_replace('/[^a-z0-9\-]/i', '_', $group);
$cacheFile = $cacheDir . '/tle_' . $cacheKey . '.json';

$readCache = static function (string $file): ?string {
    if (!is_file($file)) {
        return null;
    }

    $data = @file_get_contents($file);
    return $data === false ? null : $data;
};

$fetchRemote = static function (string $url): array {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 12,
        CURLOPT_CONNECTTIMEOUT => 6,
        CURLOPT_USERAGENT => 'NORAD-Surveillance-Terminal/1.0',
    ]);

    $body = curl_exec($ch);
    $errNo = curl_errno($ch);
    $errMsg = curl_error($ch);
    $status = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($errNo !== 0) {
        return [false, null, 'cURL error: ' . $errMsg];
    }

    if ($status < 200 || $status >= 300 || !is_string($body) || trim($body) === '') {
        return [false, null, 'HTTP error: ' . $status];
    }

    return [true, $body, null];
};

$isCacheFresh = is_file($cacheFile) && (time() - (int)filemtime($cacheFile) < $ttlSeconds);
$rawTle = null;
$source = 'remote';

if ($isCacheFresh) {
    $rawTle = $readCache($cacheFile);
    $source = 'cache';
}

if ($rawTle === null) {
    [$ok, $remoteData, $error] = $fetchRemote($endpointMap[$group]);

    if ($ok) {
        $rawTle = $remoteData;
        @file_put_contents($cacheFile, $remoteData, LOCK_EX);
        $source = 'remote';
    } else {
        $rawTle = $readCache($cacheFile);
        $source = 'stale-cache';

        if ($rawTle === null) {
            http_response_code(502);
            echo json_encode(['error' => $error ?? 'Failed to fetch TLE data'], JSON_PRETTY_PRINT);
            exit;
        }
    }
}

$lines = preg_split('/\r\n|\r|\n/', trim((string)$rawTle)) ?: [];
$clean = [];

for ($i = 0; $i < count($lines); $i += 3) {
    $name = trim((string)($lines[$i] ?? ''));
    $tle1 = trim((string)($lines[$i + 1] ?? ''));
    $tle2 = trim((string)($lines[$i + 2] ?? ''));

    if ($name === '' || !str_starts_with($tle1, '1 ') || !str_starts_with($tle2, '2 ')) {
        continue;
    }

    $noradId = trim(substr($tle1, 2, 5));
    $clean[] = [
        'name' => $name,
        'tle1' => $tle1,
        'tle2' => $tle2,
        'norad_id' => $noradId,
    ];
}

header('X-Cache-Source: ' . $source);
echo json_encode($clean, JSON_UNESCAPED_SLASHES);
