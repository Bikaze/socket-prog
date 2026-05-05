import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 9090

DEPARTMENTS = {
    1: "Computer Science",
    2: "Electrical & Electronics Engineering",
    3: "Civil Engineering",
    4: "Mechanical Engineering",
    5: "Information & Communication Technology",
    6: "Environmental Engineering",
    7: "Architecture",
}

DATABASE = [
    {"dept_no": 1, "first_name": "Jean", "last_name": "Mugisha", "phone": "+250 781 234 567", "email": "jean.mugisha@ur.ac.rw"},
    {"dept_no": 1, "first_name": "Alice", "last_name": "Umutoni", "phone": "+250 782 345 678", "email": "alice.umutoni@ur.ac.rw"},
    {"dept_no": 1, "first_name": "Pierre", "last_name": "Niyonsaba", "phone": "+250 783 456 789", "email": "pierre.niyonsaba@ur.ac.rw"},
    {"dept_no": 1, "first_name": "Marie", "last_name": "Gakwaya", "phone": "+250 784 567 890", "email": "marie.gakwaya@ur.ac.rw"},
    {"dept_no": 2, "first_name": "Patrick", "last_name": "Habimana", "phone": "+250 785 678 901", "email": "patrick.habimana@ur.ac.rw"},
    {"dept_no": 2, "first_name": "Diane", "last_name": "Uwimana", "phone": "+250 786 789 012", "email": "diane.uwimana@ur.ac.rw"},
    {"dept_no": 2, "first_name": "Eric", "last_name": "Nkurunziza", "phone": "+250 787 890 123", "email": "eric.nkurunziza@ur.ac.rw"},
    {"dept_no": 3, "first_name": "Grace", "last_name": "Mukamana", "phone": "+250 788 901 234", "email": "grace.mukamana@ur.ac.rw"},
    {"dept_no": 3, "first_name": "Paul", "last_name": "Bizimana", "phone": "+250 789 012 345", "email": "paul.bizimana@ur.ac.rw"},
    {"dept_no": 3, "first_name": "Solange", "last_name": "Nyiramana", "phone": "+250 780 123 456", "email": "solange.nyiramana@ur.ac.rw"},
    {"dept_no": 4, "first_name": "Robert", "last_name": "Nsanzimana", "phone": "+250 781 234 901", "email": "robert.nsanzimana@ur.ac.rw"},
    {"dept_no": 4, "first_name": "Yvonne", "last_name": "Ingabire", "phone": "+250 782 345 012", "email": "yvonne.ingabire@ur.ac.rw"},
    {"dept_no": 5, "first_name": "Claude", "last_name": "Hakizimana", "phone": "+250 783 456 123", "email": "claude.hakizimana@ur.ac.rw"},
    {"dept_no": 5, "first_name": "Celine", "last_name": "Uwitonze", "phone": "+250 784 567 234", "email": "celine.uwitonze@ur.ac.rw"},
    {"dept_no": 5, "first_name": "Joseph", "last_name": "Ndayambaje", "phone": "+250 785 678 345", "email": "joseph.ndayambaje@ur.ac.rw"},
    {"dept_no": 6, "first_name": "Anita", "last_name": "Mukashyaka", "phone": "+250 786 789 456", "email": "anita.mukashyaka@ur.ac.rw"},
    {"dept_no": 6, "first_name": "Denis", "last_name": "Rutaganda", "phone": "+250 787 890 567", "email": "denis.rutaganda@ur.ac.rw"},
    {"dept_no": 7, "first_name": "Judith", "last_name": "Nyirahabimana", "phone": "+250 788 901 678", "email": "judith.nyirahabimana@ur.ac.rw"},
    {"dept_no": 7, "first_name": "Samuel", "last_name": "Gasana", "phone": "+250 789 012 789", "email": "samuel.gasana@ur.ac.rw"},
    {"dept_no": 7, "first_name": "Leonie", "last_name": "Uwera", "phone": "+250 780 123 890", "email": "leonie.uwera@ur.ac.rw"},
]


def handle_list_all():
    rows = []
    for r in DATABASE:
        dept_name = DEPARTMENTS.get(r["dept_no"], "Unknown")
        rows.append(
            f"  Dept {r['dept_no']:>2} ({dept_name:<42}) | "
            f"{r['first_name']:<10} {r['last_name']:<18} | "
            f"{r['phone']:<20} | {r['email']}"
        )
    header = (
        f"  {'Dept':<48} | {'Name':<30} | {'Phone':<20} | Email\n"
        f"  {'-'*48}-+-{'-'*30}-+-{'-'*20}-+-{'-'*30}"
    )
    return "ALL RECORDS\n" + header + "\n" + "\n".join(rows)


def handle_email_by_name(first_name, last_name):
    first_name = first_name.strip().title()
    last_name = last_name.strip().title()
    for r in DATABASE:
        if r["first_name"] == first_name and r["last_name"] == last_name:
            return f"Email for {first_name} {last_name}: {r['email']}"
    return f"ERROR: No record found for '{first_name} {last_name}'."


def handle_email_by_lastname_dept(last_name, dept_no):
    last_name = last_name.strip().title()
    try:
        dept_no = int(dept_no)
    except ValueError:
        return "ERROR: Department number must be an integer."
    if dept_no not in DEPARTMENTS:
        return f"ERROR: Department number {dept_no} does not exist."
    matches = [r for r in DATABASE if r["last_name"] == last_name and r["dept_no"] == dept_no]
    if not matches:
        return f"ERROR: No record found for last name '{last_name}' in dept {dept_no}."
    lines = [f"Email(s) for {last_name} in {DEPARTMENTS[dept_no]}:"]
    for r in matches:
        lines.append(f"  {r['first_name']} {r['last_name']}: {r['email']}")
    return "\n".join(lines)


def handle_phone_by_name(first_name, last_name):
    first_name = first_name.strip().title()
    last_name = last_name.strip().title()
    for r in DATABASE:
        if r["first_name"] == first_name and r["last_name"] == last_name:
            return f"Phone for {first_name} {last_name}: {r['phone']}"
    return f"ERROR: No record found for '{first_name} {last_name}'."


def handle_list_by_dept(dept_no):
    try:
        dept_no = int(dept_no)
    except ValueError:
        return "ERROR: Department number must be an integer."
    if dept_no not in DEPARTMENTS:
        return f"ERROR: Department number {dept_no} does not exist."
    members = [r for r in DATABASE if r["dept_no"] == dept_no]
    if not members:
        return f"No records found in department {dept_no}."
    lines = [f"Members of {DEPARTMENTS[dept_no]} (Dept {dept_no}):"]
    lines.append(f"  {'Name':<30} | {'Phone':<20} | Email")
    lines.append(f"  {'-'*30}-+-{'-'*20}-+-{'-'*30}")
    for r in members:
        lines.append(f"  {r['first_name'] + ' ' + r['last_name']:<30} | {r['phone']:<20} | {r['email']}")
    return "\n".join(lines)


HELP_TEXT = """\
UR-CST Directory Server — Protocol Reference
=============================================

All requests are newline-terminated JSON objects sent over TCP.
All responses are plain text terminated by a "< <END> >" sentinel line (no spaces).

─────────────────────────────────────────────────────────────────
ACTION: help
─────────────────────────────────────────────────────────────────
  Request : {"action": "help"}
  Response: This help text.

─────────────────────────────────────────────────────────────────
ACTION: list_all
─────────────────────────────────────────────────────────────────
  Request : {"action": "list_all"}
  Response: Formatted table of every record in the database.
  Example response (truncated):
    ALL RECORDS
      Dept  1 (Computer Science ...) | Jean       Mugisha            | +250 781 234 567     | jean.mugisha@ur.ac.rw
      ...

─────────────────────────────────────────────────────────────────
ACTION: email_by_name
─────────────────────────────────────────────────────────────────
  Request : {"action": "email_by_name", "first_name": "<str>", "last_name": "<str>"}
  Required: first_name, last_name
  Response (success): "Email for <First> <Last>: <email>"
  Response (not found): "ERROR: No record found for '<First> <Last>'."
  Response (missing field): "ERROR: 'first_name' and 'last_name' are required."

─────────────────────────────────────────────────────────────────
ACTION: email_by_lastname_dept
─────────────────────────────────────────────────────────────────
  Request : {"action": "email_by_lastname_dept", "last_name": "<str>", "dept_no": <int>}
  Required: last_name, dept_no (integer 1–7)
  Response (success): "Email(s) for <Last> in <Dept Name>:\\n  <First> <Last>: <email>\\n  ..."
  Response (not found): "ERROR: No record found for last name '<Last>' in dept <N>."
  Response (bad dept):  "ERROR: Department number <N> does not exist."

─────────────────────────────────────────────────────────────────
ACTION: phone_by_name
─────────────────────────────────────────────────────────────────
  Request : {"action": "phone_by_name", "first_name": "<str>", "last_name": "<str>"}
  Required: first_name, last_name
  Response (success): "Phone for <First> <Last>: <phone>"
  Response (not found): "ERROR: No record found for '<First> <Last>'."

─────────────────────────────────────────────────────────────────
ACTION: list_by_dept
─────────────────────────────────────────────────────────────────
  Request : {"action": "list_by_dept", "dept_no": <int>}
  Required: dept_no (integer 1–7)
  Response (success): Formatted table of all members in the department.
  Response (bad dept): "ERROR: Department number <N> does not exist."

─────────────────────────────────────────────────────────────────
AVAILABLE DEPARTMENTS
─────────────────────────────────────────────────────────────────
  1 — Computer Science
  2 — Electrical & Electronics Engineering
  3 — Civil Engineering
  4 — Mechanical Engineering
  5 — Information & Communication Technology
  6 — Environmental Engineering
  7 — Architecture

─────────────────────────────────────────────────────────────────
ERROR SHAPES
─────────────────────────────────────────────────────────────────
  All error responses begin with "ERROR:" and are plain strings.
  "ERROR: Malformed request — expected JSON."   (unparseable input)
  "ERROR: Unknown action '<action>'."           (unrecognised action)
  "ERROR: '<field>' and '<field>' are required." (missing fields)
  "ERROR: Department number must be an integer." (bad dept_no type)
  "ERROR: Department number <N> does not exist." (dept_no out of range)
  "ERROR: No record found for ..."              (lookup miss)
"""


def dispatch(request_str):
    try:
        req = json.loads(request_str)
    except json.JSONDecodeError:
        return "ERROR: Malformed request — expected JSON."

    action = req.get("action", "")

    if action == "help":
        return HELP_TEXT

    elif action == "list_all":
        return handle_list_all()

    elif action == "email_by_name":
        first = req.get("first_name", "").strip()
        last = req.get("last_name", "").strip()
        if not first or not last:
            return "ERROR: 'first_name' and 'last_name' are required."
        return handle_email_by_name(first, last)

    elif action == "email_by_lastname_dept":
        last = req.get("last_name", "").strip()
        dept = req.get("dept_no", "")
        if not last or dept == "":
            return "ERROR: 'last_name' and 'dept_no' are required."
        return handle_email_by_lastname_dept(last, dept)

    elif action == "phone_by_name":
        first = req.get("first_name", "").strip()
        last = req.get("last_name", "").strip()
        if not first or not last:
            return "ERROR: 'first_name' and 'last_name' are required."
        return handle_phone_by_name(first, last)

    elif action == "list_by_dept":
        dept = req.get("dept_no", "")
        if dept == "":
            return "ERROR: 'dept_no' is required."
        return handle_list_by_dept(dept)

    else:
        return f"ERROR: Unknown action '{action}'."


def client_handler(conn, addr):
    print(f"[+] Connected: {addr}")
    try:
        with conn:
            while True:
                data = b""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        return
                    data += chunk
                    if data.endswith(b"\n"):
                        break
                request_str = data.decode("utf-8").strip()
                if not request_str:
                    continue
                response = dispatch(request_str)
                conn.sendall((response + "\n<<END>>\n").encode("utf-8"))
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        print(f"[-] Disconnected: {addr}")


def main():
    print(f"[*] UR-CST Directory Server starting on {HOST}:{PORT}")
    print(f"[*] {len(DATABASE)} records loaded across {len(DEPARTMENTS)} departments.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(10)
        print(f"[*] Listening — press Ctrl+C to stop.\n")
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)
            t.start()


if __name__ == "__main__":
    main()
