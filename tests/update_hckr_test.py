import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('update_hckr', ROOT / 'scripts/update_hckr.py')
update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update)
FORMULA = 'class Hckr < Formula\n  head "https://github.com/kzzzld/hckr.git", branch: "main"\nend\n'
CHECKSUM = 'a' * 64


class UpdateTest(unittest.TestCase):
    def test_first_release_preserves_head(self):
        text = update.update_formula(FORMULA, 'v0.1.0', CHECKSUM)
        self.assertIn('/v0.1.0/hckr-0.1.0.tar.gz', text)
        self.assertIn(f'sha256 "{CHECKSUM}"', text)
        self.assertIn('  head ', text)
        self.assertEqual(update.update_formula(text, 'v0.1.0', CHECKSUM), text)

    def test_upgrades_and_guards(self):
        first = update.update_formula(FORMULA, 'v1.2.0', CHECKSUM)
        second = update.update_formula(first, 'v1.3.0', 'b' * 64)
        self.assertEqual(second.count('  url '), 1)
        self.assertEqual(second.count('  sha256 '), 1)
        self.assertNotIn('v1.2.0', second)
        for tag, checksum in (('v1.1.0', CHECKSUM), ('v1.2.0', 'b' * 64),
                              ('v01.3.0', CHECKSUM), ('v1.3.0', 'not-a-checksum')):
            with self.subTest(tag=tag, checksum=checksum):
                with self.assertRaises(ValueError):
                    update.update_formula(first, tag, checksum)

    def test_checksums(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / 'hckr-0.1.0.tar.gz'
            archive.write_bytes(b'source release')
            checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(update.verify_archive(archive, f'{checksum}  {archive.name}\n'), checksum)
            for manifest in ('', f'{CHECKSUM}  {archive.name}\n',
                             f'{checksum}  other.tar.gz\n',
                             f'{checksum}  {archive.name}\n' * 2):
                with self.assertRaises(ValueError):
                    update.verify_archive(archive, manifest)


if __name__ == '__main__':
    unittest.main()
