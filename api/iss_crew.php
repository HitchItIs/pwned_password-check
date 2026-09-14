<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

$cacheDir = dirname(__DIR__) . '/cache';
if (!is_dir($cacheDir)) {
    @mkdir($cacheDir, 0775, true);
}

$cacheFile = $cacheDir . '/iss_crew.json';
$ttlSeconds = 300;
$url = 'http://api.open-notify.org/astros.json';

$readCache = static function (string $file): ?string {
    if (!is_file($file)) {
        return null;
    }
    $data = @file_get_contents($file);
    return $data === false ? null : $data;
};

if (is_file($cacheFile) && (time() - (int)filemtime($cacheFile) < $ttlSeconds)) {
    $cached = $readCache($cacheFile);
    if ($cached !== null) {
        header('X-Cache-Source: cache');
        echo $cached;
        exit;
    }
}

$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_TIMEOUT => 10,
    CURLOPT_CONNECTTIMEOUT => 4,
    CURLOPT_USERAGENT => 'NORAD-Surveillance-Terminal/1.0',
]);

$body = curl_exec($ch);
$errNo = curl_errno($ch);
$errMsg = curl_error($ch);
$status = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($errNo !== 0 || $status < 200 || $status >= 300 || !is_string($body) || trim($body) === '') {
    $cached = $readCache($cacheFile);
    if ($cached !== null) {
        header('X-Cache-Source: stale-cache');
        echo $cached;
        exit;
    }

    http_response_code(502);
    echo json_encode(['error' => $errNo !== 0 ? $errMsg : 'Open Notify unavailable'], JSON_PRETTY_PRINT);
    exit;
}

@file_put_contents($cacheFile, $body, LOCK_EX);
header('X-Cache-Source: remote');
echo $body;
