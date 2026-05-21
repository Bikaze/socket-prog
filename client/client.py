import socket
import json

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9090

DEPARTMENTS = {
    1: "Computer Engineering",
    2: "Computer Science",
    3: "Information Systems",
    4: "Information Technology",
}

MENU = """
╔══════════════════════════════════════════════════════════╗
║        UR-CST Staff/Student Directory Client             ║
╠══════════════════════════════════════════════════════════╣
║  1. List all records                                     ║
║  2. Get email by First Name + Last Name                  ║
║  3. Get email by Last Name + Department Number           ║
║  4. Get phone number by First Name + Last Name           ║
║  5. List all members in a Department                     ║
║  6. Show department list                                 ║
║  7. Server protocol help                                 ║
║  0. Exit                                                 ║
╚══════════════════════════════════════════════════════════╝"""


def send_request(sock, payload: dict) -> str:
    message = json.dumps(payload) + "\n"
    sock.sendall(message.encode("utf-8"))

    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionResetError("Server closed the connection unexpectedly.")
        response += chunk
        if b"<<END>>" in response:
            break

    decoded = response.decode("utf-8")
    # Strip the sentinel
    decoded = decoded.replace("<<END>>", "").strip()
    return decoded


def prompt(label: str) -> str:
    value = input(f"  {label}: ").strip()
    return value


def show_departments():
    print("\n  Available Departments:")
    for no, name in DEPARTMENTS.items():
        print(f"    [{no}] {name}")


def run_menu(sock):
    while True:
        print(MENU)
        choice = input("  Select an option: ").strip()

        if choice == "0":
            print("\n  Goodbye!\n")
            break

        elif choice == "1":
            payload = {"action": "list_all"}

        elif choice == "2":
            first = prompt("First name")
            last = prompt("Last name")
            if not first or not last:
                print("  [!] Both first and last name are required.\n")
                continue
            payload = {"action": "email_by_name", "first_name": first, "last_name": last}

        elif choice == "3":
            show_departments()
            last = prompt("Last name")
            dept_raw = prompt("Department number")
            if not last or not dept_raw:
                print("  [!] Last name and department number are required.\n")
                continue
            try:
                dept_no = int(dept_raw)
            except ValueError:
                print("  [!] Department number must be an integer.\n")
                continue
            payload = {"action": "email_by_lastname_dept", "last_name": last, "dept_no": dept_no}

        elif choice == "4":
            first = prompt("First name")
            last = prompt("Last name")
            if not first or not last:
                print("  [!] Both first and last name are required.\n")
                continue
            payload = {"action": "phone_by_name", "first_name": first, "last_name": last}

        elif choice == "5":
            show_departments()
            dept_raw = prompt("Department number")
            try:
                dept_no = int(dept_raw)
            except ValueError:
                print("  [!] Department number must be an integer.\n")
                continue
            payload = {"action": "list_by_dept", "dept_no": dept_no}

        elif choice == "6":
            show_departments()
            continue

        elif choice == "7":
            payload = {"action": "help"}

        else:
            print("  [!] Invalid option. Please choose 0–7.\n")
            continue

        try:
            result = send_request(sock, payload)
            print(f"\n{'─'*62}")
            print(result)
            print(f"{'─'*62}\n")
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            print(f"\n  [!] Connection error: {e}")
            break


def main():
    print(f"\n  Connecting to {SERVER_HOST}:{SERVER_PORT} ...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((SERVER_HOST, SERVER_PORT))
            sock.settimeout(None)
            print("  Connected.\n")
            run_menu(sock)
    except (ConnectionRefusedError, OSError):
        print(f"  [!] Could not connect to server at {SERVER_HOST}:{SERVER_PORT}.")
        print("      Make sure server/server.py is running first.\n")


if __name__ == "__main__":
    main()
