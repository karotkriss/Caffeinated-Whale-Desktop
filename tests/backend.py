import unittest
import subprocess
import time
import colorama


class TestFrappeInstanceInfo(unittest.TestCase):
    def setUp(self):
        self.project_name = "test"
        self.site_name = "dev.complaints.localhost"

    def test_get_sites(self):
        self.print_test_name("Get Sites")
        start_time = time.time()
        result = subprocess.run(
            ["python", "backend/frappe_instance_info.py", "-p", self.project_name, "--get-sites"],
            capture_output=True,
            text=True,
        )
        end_time = time.time()
        print(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertGreater(len(result.stdout.strip().split("\n")), 0)
        self.print_test_result("PASS", end_time - start_time)

    def test_get_site_app(self):
        self.print_test_name("Get Site App")
        start_time = time.time()
        result = subprocess.run(
            ["python", "backend/frappe_instance_info.py", "-p", self.project_name, "--get-site-app", self.site_name],
            capture_output=True,
            text=True,
        )
        end_time = time.time()
        print(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertGreater(len(result.stdout.strip().split("\n")), 0)
        self.print_test_result("PASS", end_time - start_time)

    def test_get_apps(self):
        self.print_test_name("Get Apps")
        start_time = time.time()
        result = subprocess.run(
            ["python", "backend/frappe_instance_info.py", "-p", self.project_name, "--get-apps"],
            capture_output=True,
            text=True,
        )
        end_time = time.time()
        print(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertGreater(len(result.stdout.strip().split("\n")), 0)
        self.print_test_result("PASS", end_time - start_time)

    def test_get_site_info(self):
        self.print_test_name("Get Site Info")
        start_time = time.time()
        result = subprocess.run(
            ["python", "backend/frappe_instance_info.py", "-p", self.project_name, "--get-site-info", self.site_name],
            capture_output=True,
            text=True,
        )
        end_time = time.time()
        print(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertGreater(len(result.stdout.strip().split("\n")), 0)
        self.print_test_result("PASS", end_time - start_time)
        
        
    def test_get_site_info(self):
        self.print_test_name("Get *")
        start_time = time.time()
        result = subprocess.run(
            ["python", "backend/frappe_instance_info.py"],
            capture_output=True,
            text=True,
        )
        end_time = time.time()
        print(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertGreater(len(result.stdout.strip().split("\n")), 0)
        self.print_test_result("PASS", end_time - start_time)

    def print_header(self, message):
        print(colorama.Fore.GREEN + "=" * 80)
        print(message.center(80))
        print("=" * 80 + colorama.Style.RESET_ALL)

    def print_test_name(self, message):
        print(colorama.Fore.BLUE + message + colorama.Style.RESET_ALL)

    def print_test_result(self, result, duration):
        if isinstance(duration, (int, float)):
            print(f"{result} ({duration:.2f} seconds)" + colorama.Style.RESET_ALL)
        else:
            print(f"{result} (Error: {duration})" + colorama.Style.RESET_ALL)


if __name__ == "__main__":
    unittest.main()

