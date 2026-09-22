import unittest
from security import zero_buffer, get_hash

class TestSecurity(unittest.TestCase):
    def test_zero_buffer(self):
        buf = bytearray(b"sensitive_password")
        zero_buffer(buf)
        self.assertEqual(buf, bytearray(len(b"sensitive_password")))
        self.assertTrue(all(b == 0 for b in buf))

    def test_get_hash(self):
        password = bytearray(b"test_password")
        # SHA1 of "test_password"
        # Hex: 9fb7fe1217aed442b04c0f5e43b5d5a7d3287097
        expected_hash = "9FB7FE1217AED442B04C0F5E43B5D5A7D3287097"
        self.assertEqual(get_hash(password), expected_hash)

if __name__ == '__main__':
    unittest.main()
