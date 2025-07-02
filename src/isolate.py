import subprocess

def isolate_init(box_id: int):
    box_path = subprocess.run(["isolate", "--box-id", str(box_id), "--init"], check=True, text=True, capture_output=True).stdout.strip()
    return box_path

def isolate_run(cmd: list[str], box_id: int, box_path: str, time_limit:int = 1, memory_limit: int = 64, stdin=None, meta_file: str = "meta.txt"):
    args = [
        "isolate",
        "--box-id", str(box_id),
        "--run",
        # "--dir=/home/enrico/.cargo", # CAMBIARE USER
        # "--dir=/home/enrico/.rustup",
        "--dir=/usr/bin",
        "--dir=/usr/lib",
        "--dir=/usr/include",
        # "--env=PATH=/usr/lib/jvm/default/bin:/usr/bin:/bin",
        # "--env=JAVA_HOME=/usr/lib/jvm/default", # BOH NON FUNZIONA
        # "--env=CARGO_HOME=/home/enrico/.cargo", # CAMBIARE NOME
        # "--env=RUSTUP_HOME=/home/enrico/.rustup",
        "--processes=50",
        "--meta", f"{box_path}/{meta_file}",
        # "--time", str(time_limit),
        # "--mem", str(memory_limit * 1024),
        "--stdin", stdin if stdin else "/dev/null",
        # "--stdout", "stdout.txt",
        # "--stderr", "stderr.txt",
        "--",
    ] + cmd
    result = subprocess.run(args, cwd=f"{box_path}/box")
    return result.returncode

def isolate_cleanup(box_id: int):
    subprocess.run(["isolate", "--box-id", str(box_id), "--cleanup"], check=True)