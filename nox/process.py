import subprocess
import threading

class NoxProcess:
    def __init__(self, proc: subprocess.Popen):
        self._proc = proc
        self._output = []
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._read, daemon=True)
        self._thread.start()

    def _read(self):
        for line in self._proc.stdout:
            decoded = line.decode("utf-8", errors="replace").rstrip("\n")
            with self._lock:
                self._output.append(decoded)

    def output(self):
        with self._lock:
            return list(self._output)

    def kill(self):
        self._proc.kill()

    def stop(self):
        self._proc.terminate()

    def wait(self):
        self._proc.wait()
        self._thread.join()
        return self._proc.returncode

    def alive(self):
        return self._proc.poll() is None

    def get(self, attr: str):
        methods = {
            "output": self.output,
            "kill": self.kill,
            "stop": self.stop,
            "wait": self.wait,
            "alive": self.alive,
        }
        if attr in methods:
            return methods[attr]
        raise RuntimeError(f"Process has no attribute '{attr}'")


def _make_process_module():
    def run(cmd, *args):
        proc = subprocess.Popen(
            [cmd, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=False,  # читаем байты
        )
        return NoxProcess(proc)

    def shell(cmd):
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return NoxProcess(proc)

    return {
        "run": run,
        "shell": shell,
    }