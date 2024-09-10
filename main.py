import schedule
import time

from config_check import check_config_version
from submissions_manager import start_listen_for_submissions

if __name__ == "__main__":
    # code = "#include <stdio.h>\nint main() { char input[100]; scanf(\"%99s\", input); printf(\"%s\\n\", input); return 0; }"
    # code = "fn main() { let mut input = String::new(); std::io::stdin().read_line(&mut input).expect(\"Failed to read line\"); print!(\"{}\", input); }"
    # code = "import java.util.Scanner; public class Main { public static void main(String[] args) { Scanner scanner = new Scanner(System.in); String input = scanner.nextLine(); System.out.println(input); } }"
    # code = "[a, b] = input().split(' ')\nprint(int(a) + int(b))"
    # result = execute_code_locally(code, 1, 'python')
    # print(result)

    schedule.every(30).seconds.do(check_config_version)
    start_listen_for_submissions()
    
    while True:
        schedule.run_pending()
        time.sleep(0.1)