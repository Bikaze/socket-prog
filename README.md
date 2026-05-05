# UR-CST Directory Server

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![TCP](https://img.shields.io/badge/Protocol-TCP%20Socket-00897B?style=flat-square&logo=cloudflare&logoColor=white)
![Threading](https://img.shields.io/badge/Concurrency-Multi--threaded-8E24AA?style=flat-square&logo=processwire&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-F57C00?style=flat-square)
![University](https://img.shields.io/badge/UR-CST-College%20of%20Science%20%26%20Technology-1565C0?style=flat-square)

A distributed TCP client-server directory application for the **University of Rwanda — College of Science and Technology**. Look up staff and student emails, phone numbers, and department rosters over the network in real time.

---

## Project Structure

```
socket-prog/
├── server/
│   └── server.py      # Multi-threaded TCP server + in-memory database
└── client/
    └── client.py      # Interactive CLI client
```

---

## How It Works

```
┌─────────────┐   JSON request (TCP)    ┌──────────────────────┐
│  client.py  │ ──────────────────────► │     server.py        │
│  (CLI menu) │ ◄────────────────────── │  dispatch() + DB     │
└─────────────┘   plain-text response   └──────────────────────┘
```

1. The **server** binds to port `9090` and spawns a new thread per client connection.
2. The **client** sends a newline-terminated JSON object describing the query.
3. The **server** routes it through `dispatch()`, queries the in-memory database, and replies with plain text ending in `<<END>>`.
4. The **client** strips the sentinel and prints the result.

---

## Quick Start

> No virtual environment or third-party packages needed — pure Python stdlib.

### 1. Start the server

```bash
python3 server/server.py
```

```
[*] UR-CST Directory Server starting on 0.0.0.0:9090
[*] 20 records loaded across 7 departments.
[*] Listening — press Ctrl+C to stop.
```

### 2. Connect with the client (new terminal)

```bash
python3 client/client.py
```

You will see the interactive menu:

```
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
╚══════════════════════════════════════════════════════════╝
```

---

## Departments

| # | Department |
|---|------------|
| 1 | Computer Science |
| 2 | Electrical & Electronics Engineering |
| 3 | Civil Engineering |
| 4 | Mechanical Engineering |
| 5 | Information & Communication Technology |
| 6 | Environmental Engineering |
| 7 | Architecture |

---

## Alternative: Query with `nc`

You can talk to the server directly without the client using netcat:

```bash
# List all records
echo '{"action": "list_all"}' | nc 127.0.0.1 9090

# Get email by name
echo '{"action": "email_by_name", "first_name": "Jean", "last_name": "Mugisha"}' | nc 127.0.0.1 9090

# Get phone by name
echo '{"action": "phone_by_name", "first_name": "Alice", "last_name": "Umutoni"}' | nc 127.0.0.1 9090

# Email by last name + department
echo '{"action": "email_by_lastname_dept", "last_name": "Uwimana", "dept_no": 2}' | nc 127.0.0.1 9090

# List department members
echo '{"action": "list_by_dept", "dept_no": 1}' | nc 127.0.0.1 9090

# Protocol help
echo '{"action": "help"}' | nc 127.0.0.1 9090
```

> Install netcat if missing: `sudo apt install netcat-openbsd`

---

## Wire Protocol

| Layer | Detail |
|-------|--------|
| Transport | TCP on port `9090` |
| Request | Newline-terminated JSON: `{"action": "<name>", ...}\n` |
| Response | Plain text ending with `\n<<END>>\n` |
| Encoding | UTF-8 |

All errors begin with `ERROR:` so clients can detect them without parsing structure.

---

## Server Functions at a Glance

| Function | Input | Returns |
|----------|-------|---------|
| `handle_list_all()` | — | Full formatted table of all 20 records |
| `handle_email_by_name(first, last)` | Two name strings | Email address or error |
| `handle_email_by_lastname_dept(last, dept_no)` | Last name + dept number | Email(s) or error |
| `handle_phone_by_name(first, last)` | Two name strings | Phone number or error |
| `handle_list_by_dept(dept_no)` | Department number | Table of all dept members or error |
| `dispatch(request_str)` | Raw JSON string from socket | Routes to the correct handler above |
| `client_handler(conn, addr)` | Socket + client address | Reads requests, writes responses in a loop |
| `main()` | — | Starts the server, spawns threads per client |
