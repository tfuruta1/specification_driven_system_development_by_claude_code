import unittest
import sys
import os
from io import StringIO
from unittest.mock import patch

# Add the project directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestMain(unittest.TestCase):
    
    def test_main_function_exists(self):
        """Test that main function exists in main module"""
        try:
            import main
            self.assertTrue(hasattr(main, 'main'), "main function should exist in main module")
        except ImportError:
            self.fail("main.py module should exist")
    
    def test_main_function_outputs_hello_world(self):
        """Test that main function outputs 'Hello World'"""
        try:
            import main
            # Capture stdout to verify output
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main.main()
                output = mock_stdout.getvalue().strip()
                self.assertEqual(output, "Hello World", 
                               "main function should output 'Hello World'")
        except ImportError:
            self.fail("main.py module should exist")
    
    def test_script_execution(self):
        """Test that main.py can be executed as a script"""
        # This test checks if running main.py as a script produces the expected output
        import subprocess
        import os
        
        main_py_path = os.path.join(os.path.dirname(__file__), 'main.py')
        
        try:
            result = subprocess.run([sys.executable, main_py_path], 
                                  capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, 
                           "main.py should execute without errors")
            self.assertEqual(result.stdout.strip(), "Hello World",
                           "Script execution should output 'Hello World'")
        except FileNotFoundError:
            self.fail("main.py file should exist")
        except subprocess.TimeoutExpired:
            self.fail("main.py execution should not timeout")

if __name__ == '__main__':
    unittest.main()