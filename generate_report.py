"""
Report generator for the Socket Programming lab assignment.
Run:  python generate_report.py
Output: report.pdf in the same directory.
"""

import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
OUTPUT_PATH = os.path.join(BASE_DIR, "report.pdf")
UR_LOGO = os.path.join(SCREENSHOTS_DIR, "ur_logo.png")

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm

TODAY = date.today().strftime("%B %d, %Y")  # e.g. May 21, 2026

# ── Colour palette ──────────────────────────────────────────────────────────
UR_BLUE  = colors.HexColor("#003087")
UR_GOLD  = colors.HexColor("#F5A800")
LIGHT_BG = colors.HexColor("#F2F6FC")
MID_GREY = colors.HexColor("#555555")
CODE_BG  = colors.HexColor("#1E1E2E")
CODE_FG  = colors.HexColor("#CDD6F4")

# ── Styles ───────────────────────────────────────────────────────────────────
base_styles = getSampleStyleSheet()

def style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)

S = {
    "cover_uni":    style("CoverUni",   fontSize=13, leading=18, alignment=TA_CENTER,
                          textColor=UR_BLUE, fontName="Helvetica-Bold"),
    "cover_title":  style("CoverTitle", fontSize=16, leading=22, alignment=TA_CENTER,
                          textColor=UR_BLUE, fontName="Helvetica-Bold", spaceAfter=6),
    "cover_sub":    style("CoverSub",   fontSize=12, leading=16, alignment=TA_CENTER,
                          textColor=MID_GREY, fontName="Helvetica"),
    "cover_date":   style("CoverDate",  fontSize=11, leading=14, alignment=TA_CENTER,
                          textColor=MID_GREY, fontName="Helvetica-Oblique"),
    "h1":           style("H1", fontSize=14, leading=20, spaceBefore=14, spaceAfter=6,
                          textColor=UR_BLUE, fontName="Helvetica-Bold",
                          borderPad=4),
    "h2":           style("H2", fontSize=12, leading=16, spaceBefore=10, spaceAfter=4,
                          textColor=UR_BLUE, fontName="Helvetica-Bold"),
    "body":         style("Body", fontSize=10.5, leading=15, alignment=TA_JUSTIFY,
                          textColor=colors.black, fontName="Helvetica",
                          spaceAfter=6),
    "code":         style("Code", fontSize=9, leading=13, fontName="Courier",
                          textColor=CODE_FG, backColor=CODE_BG,
                          leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4,
                          borderPad=6),
    "caption":      style("Caption", fontSize=9, leading=12, alignment=TA_CENTER,
                          textColor=MID_GREY, fontName="Helvetica-Oblique",
                          spaceAfter=10),
    "table_hdr":    style("TblHdr", fontSize=10, leading=13, alignment=TA_CENTER,
                          textColor=colors.white, fontName="Helvetica-Bold"),
    "table_cell":   style("TblCell", fontSize=9.5, leading=13, alignment=TA_LEFT,
                          textColor=colors.black, fontName="Helvetica"),
}

# ── Helpers ──────────────────────────────────────────────────────────────────
def ss(filename, width=None, caption=None, max_height=None):
    """Return [Image, caption Paragraph] for a screenshot."""
    from PIL import Image as PILImage
    path = os.path.join(SCREENSHOTS_DIR, filename)
    if not os.path.exists(path):
        return [Paragraph(f"[Missing screenshot: {filename}]", S["caption"])]

    avail_w = PAGE_W - 2 * MARGIN
    avail_h = max_height or (PAGE_H - 4 * MARGIN)  # leave room for caption + heading

    pil = PILImage.open(path)
    orig_w, orig_h = pil.size
    aspect = orig_h / orig_w

    target_w = width or avail_w
    target_h = target_w * aspect

    # Scale down if too tall
    if target_h > avail_h:
        target_h = avail_h
        target_w = target_h / aspect

    img = Image(path, width=target_w, height=target_h)
    img.hAlign = "CENTER"
    elems = [img]
    if caption:
        elems.append(Paragraph(caption, S["caption"]))
    return elems

def p(text, s="body"):
    return Paragraph(text, S[s])

def h1(text):
    return p(text, "h1")

def h2(text):
    return p(text, "h2")

def code(text):
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(escaped, S["code"])

def hr():
    return HRFlowable(width="100%", thickness=0.8, color=UR_GOLD, spaceAfter=6)

def spacer(h=0.3):
    return Spacer(1, h * cm)

# ── Cover page ────────────────────────────────────────────────────────────────
def cover_page():
    elems = []

    # Logo
    if os.path.exists(UR_LOGO):
        logo = Image(UR_LOGO, width=4*cm, height=4*cm)
        logo.hAlign = "CENTER"
        elems.append(spacer(1.5))
        elems.append(logo)
    elems.append(spacer(0.6))

    # Institution block
    for line in [
        "UNIVERSITY OF RWANDA",
        "COLLEGE OF SCIENCE AND TECHNOLOGY",
        "SCHOOL OF ICT",
        "DEPARTMENT OF COMPUTER SCIENCE",
    ]:
        elems.append(p(line, "cover_uni"))

    elems.append(hr())
    elems.append(spacer(0.5))

    elems.append(p("Parallel and Distributed Computing", "cover_sub"))
    elems.append(spacer(0.3))
    elems.append(p("Distributed Systems Assignment Lab", "cover_title"))
    elems.append(p("Introduction to Socket Programming", "cover_title"))
    elems.append(spacer(0.5))
    elems.append(hr())
    elems.append(spacer(0.8))

    # Members table
    members = [
        ["Row No.", "Registration No.", "Names"],
        ["1",  "222004611", "Clement MUGISHA"],
        ["2",  "222014353", "Marie Mireille Irafasha"],
        ["3",  "222005615", "Joseph Bonheur Iradukunda"],
        ["4",  "222002123", "Rose Umutesi"],
        ["5",  "222019837", "Izere Bugingo Vainqueur Beryl"],
        ["6",  "222002227", "Elvis Mugisha"],
        ["7",  "222005152", "Uwineza Florance"],
        ["8",  "222018513", "Mugisha Edson"],
        ["9",  "222004590", "Sugira Herve"],
        ["10", "222008836", "Marie Claire Nisingizwe"],
        ["11", "___________", "___________________________"],  # placeholder
    ]

    col_widths = [1.5*cm, 4.5*cm, 8.5*cm]
    tbl = Table(members, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        # Header row
        ("BACKGROUND",   (0, 0), (-1, 0),  UR_BLUE),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  10),
        ("ALIGN",        (0, 0), (-1, 0),  "CENTER"),
        # Data rows
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9.5),
        ("ALIGN",        (0, 1), (0, -1),  "CENTER"),
        ("ALIGN",        (1, 1), (1, -1),  "CENTER"),
        ("ALIGN",        (2, 1), (2, -1),  "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#AAAAAA")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    elems.append(p("Group Members Participation Table", "cover_sub"))
    elems.append(spacer(0.3))
    elems.append(tbl)
    elems.append(spacer(1.0))
    elems.append(p(TODAY, "cover_date"))
    elems.append(PageBreak())
    return elems

# ── Section 1: What is a Socket? ─────────────────────────────────────────────
def section_introduction():
    return [
        h1("1. What is Socket Programming?"),
        hr(),
        p(
            "A <b>socket</b> is one endpoint of a two-way communication link between two programs "
            "running on a network. A socket is bound to a port number so that the transport layer "
            "can identify the application to which data is destined. Sockets are the fundamental "
            "building blocks of network communication — they allow processes on different machines "
            "(or the same machine) to exchange data as if they were writing to and reading from a file."
        ),
        p(
            "Socket programming is the practice of writing programs that use sockets to communicate "
            "over a network. Python exposes this through the built-in <b>socket</b> module, which "
            "provides a low-level interface directly to the operating system's networking stack."
        ),
        spacer(0.3),
        h2("1.1 TCP vs UDP"),
        p(
            "There are two dominant transport-layer protocols used with sockets:"
        ),
        p(
            "<b>TCP (Transmission Control Protocol)</b> — connection-oriented, reliable, ordered, "
            "and error-checked. Before any data is exchanged, a connection is established through "
            "a three-way handshake (SYN → SYN-ACK → ACK). Every byte sent is guaranteed to arrive "
            "in the correct order. This makes TCP ideal for applications where data integrity matters, "
            "such as our directory lookup service."
        ),
        p(
            "<b>UDP (User Datagram Protocol)</b> — connectionless, unreliable, and unordered. "
            "Packets (datagrams) are fired without establishing a connection and may arrive out of "
            "order or not at all. UDP is preferred when speed matters more than reliability, "
            "such as video streaming or online games."
        ),
        p(
            "This lab uses <b>TCP sockets</b> exclusively, matching Python's "
            "<font name='Courier'>socket.SOCK_STREAM</font> type."
        ),
        spacer(0.3),
        h2("1.2 The Client-Server Model"),
        p(
            "Socket-based applications almost always follow the <b>client-server model</b>:"
        ),
        p("&bull; The <b>server</b> is a long-running process that binds to a fixed address and "
          "port, listens for incoming connections, and serves requests."),
        p("&bull; The <b>client</b> is a shorter-lived process that knows the server's address "
          "and port, initiates the connection, sends requests, and reads responses."),
        p(
            "In our lab, <font name='Courier'>server/server.py</font> is the server and "
            "<font name='Courier'>client/client.py</font> is the client. The server holds a "
            "database of UR-CST students and staff. Clients connect and query that database over TCP."
        ),
        spacer(),
    ]

# ── Section 2: The Lab Scenario ───────────────────────────────────────────────
def section_lab_overview():
    return [
        h1("2. Lab Overview — UR-CST Staff/Student Directory"),
        hr(),
        p(
            "The School of ICT at the University of Rwanda — College of Science and Technology (UR-CST) "
            "has four departments sharing a central server:"
        ),
        p("&bull; Department of Computer Engineering"),
        p("&bull; Department of Computer Science"),
        p("&bull; Department of Information Systems"),
        p("&bull; Department of Information Technology"),
        spacer(0.2),
        p(
            "The central server stores records for every student and employee. Each record contains: "
            "department number, first name, last name, phone number, and email address. "
            "Any client (student or teacher) can connect to the server and make one of the following queries:"
        ),
        p("&bull; <b>List all records</b> — retrieve the full directory."),
        p("&bull; <b>Email by first name + last name</b> — look up a person's email directly."),
        p("&bull; <b>Email by last name + department number</b> — useful when only partial information is known."),
        p("&bull; <b>Phone by first name + last name</b> — retrieve a phone number."),
        p("&bull; <b>List all members in a department</b> — retrieve everyone in a given department."),
        spacer(),
    ]

# ── Section 3: How the Server Works ──────────────────────────────────────────
def section_server():
    elems = [
        h1("3. The Server — Binding, Listening, and Accepting Connections"),
        hr(),
        p(
            "The server side of a TCP socket application goes through four distinct steps before "
            "it can serve any client: <b>create</b>, <b>bind</b>, <b>listen</b>, and <b>accept</b>."
        ),
        spacer(0.2),
        h2("3.1 Creating and Binding the Socket"),
        p(
            "The server creates a TCP socket, sets the "
            "<font name='Courier'>SO_REUSEADDR</font> option so the port can be reused immediately "
            "after a restart, then binds to <font name='Courier'>0.0.0.0:9090</font>. "
            "Binding to <font name='Courier'>0.0.0.0</font> means the server listens on all "
            "available network interfaces."
        ),
        code(
            'srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n'
            'srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n'
            'srv.bind(("0.0.0.0", 9090))\n'
            'srv.listen(10)'
        ),
        spacer(0.2),
        h2("3.2 Server Startup — Screenshot 1"),
        p(
            "Running <font name='Courier'>python server/server.py</font> produces the following "
            "startup output, confirming the socket is bound and listening:"
        ),
        spacer(0.2),
    ]
    elems += ss("ss1_server_startup_output.png",
                caption="SS1 — Server starts, binds to 0.0.0.0:9090, and enters the listening state.")
    elems += [
        spacer(0.3),
        h2("3.3 Accepting Connections"),
        p(
            "<font name='Courier'>srv.listen(10)</font> sets the backlog — the maximum number of "
            "queued connections waiting to be accepted. The server then loops forever, calling "
            "<font name='Courier'>srv.accept()</font>, which blocks until a client connects and "
            "returns a new socket object dedicated to that client along with the client's address."
        ),
        code(
            'while True:\n'
            '    conn, addr = srv.accept()\n'
            '    t = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)\n'
            '    t.start()'
        ),
        spacer(),
    ]
    return elems

# ── Section 4: The Client — Connecting ───────────────────────────────────────
def section_client():
    elems = [
        h1("4. The Client — Connecting to the Server"),
        hr(),
        p(
            "The client creates the same type of TCP socket and calls "
            "<font name='Courier'>connect()</font> with the server's IP address and port. "
            "This triggers the TCP three-way handshake. A 5-second timeout is set before "
            "connecting so the client fails fast if the server is unreachable."
        ),
        code(
            'sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n'
            'sock.settimeout(5)\n'
            'sock.connect(("127.0.0.1", 9090))\n'
            'sock.settimeout(None)   # restore blocking mode after connect'
        ),
        spacer(0.2),
        h2("4.1 The Connection Moment — Screenshot 2"),
        p(
            "The screenshot below shows both terminals side by side at the instant a client "
            "connects. The server terminal (left) logs the client's address. The client terminal "
            "(right) confirms the connection and displays the menu."
        ),
        spacer(0.2),
    ]
    elems += ss("ss2_both_terminals_at_client_connection.png",
                caption="SS2 — Left: server logs '[+] Connected'. Right: client prints 'Connected.' and shows the menu.")
    elems += [spacer(0.3)]

    h2_menu = h2("4.2 The Client Menu — Screenshot 3")
    elems += [
        h2_menu,
        p(
            "Once connected, the client presents a menu of all supported query types. "
            "Each option maps to a different JSON action sent to the server."
        ),
        spacer(0.2),
    ]
    elems += ss("ss3_client_menu.png",
                caption="SS3 — The client menu listing all available query options (0–7).")
    elems += [spacer()]
    return elems

# ── Section 5: The Protocol — Sending and Receiving Data ─────────────────────
def section_protocol():
    elems = [
        h1("5. The Application Protocol — JSON over TCP"),
        hr(),
        p(
            "Raw TCP is just a stream of bytes — it has no concept of messages or boundaries. "
            "Our application defines its own protocol on top of TCP:"
        ),
        p("&bull; <b>Requests</b> are newline-terminated JSON objects sent by the client."),
        p("&bull; <b>Responses</b> are plain-text strings sent by the server, terminated by "
          "a special sentinel token <font name='Courier'>&lt;&lt;END&gt;&gt;</font>."),
        p(
            "The sentinel pattern is necessary because TCP is a stream protocol — the receiver "
            "does not know where one message ends and the next begins. By agreeing on a terminator, "
            "both sides know exactly when a full response has arrived."
        ),
        spacer(0.2),
        h2("5.1 Sending a Request"),
        code(
            'payload = {"action": "email_by_name", "first_name": "Jean", "last_name": "Mugisha"}\n'
            'message = json.dumps(payload) + "\\n"\n'
            'sock.sendall(message.encode("utf-8"))'
        ),
        spacer(0.2),
        h2("5.2 Receiving a Response"),
        p(
            "<font name='Courier'>recv()</font> may return less than the full response in a single "
            "call — TCP can split data across multiple packets. The client loops, accumulating "
            "chunks, until it sees the sentinel:"
        ),
        code(
            'response = b""\n'
            'while True:\n'
            '    chunk = sock.recv(4096)\n'
            '    if not chunk:\n'
            '        raise ConnectionResetError("Server closed the connection unexpectedly.")\n'
            '    response += chunk\n'
            '    if b"<<END>>" in response:\n'
            '        break'
        ),
        spacer(),
    ]
    return elems

# ── Section 6: Queries in Action ─────────────────────────────────────────────
def section_queries():
    elems = [
        h1("6. Queries in Action"),
        hr(),

        h2("6.1 List All Records — Screenshot 4"),
        p(
            "Option 1 sends <font name='Courier'>{\"action\": \"list_all\"}</font>. "
            "The server iterates over every record in the database and returns a formatted table. "
            "This is the largest payload and best illustrates the recv-loop: the response spans "
            "multiple TCP segments before the sentinel arrives."
        ),
        spacer(0.2),
    ]
    elems += ss("ss4_list_all_records.png",
                caption="SS4 — Full directory table returned by the server for the 'list_all' action.")
    elems += [
        spacer(0.4),
        h2("6.2 Email Lookup by First Name + Last Name — Screenshot 5a"),
        p(
            "Option 2 sends <font name='Courier'>{\"action\": \"email_by_name\", "
            "\"first_name\": \"...\", \"last_name\": \"...\"}</font>. "
            "The server searches the database and returns a single email address — "
            "a minimal but complete request-response cycle."
        ),
        spacer(0.2),
    ]
    elems += ss("ss5a_email_lookup_by_first_n_last_name.png",
                caption="SS5a — Email retrieved by providing first and last name.")
    elems += [
        spacer(0.4),
        h2("6.3 Email Lookup by Last Name + Department — Screenshot 5b"),
        p(
            "Option 3 sends <font name='Courier'>{\"action\": \"email_by_lastname_dept\", "
            "\"last_name\": \"...\", \"dept_no\": N}</font>. "
            "This is the second email-lookup method specified in the lab requirements — "
            "useful when only partial information is known. The <font name='Courier'>dept_no</font> "
            "field shows how integer parameters are carried inside the JSON."
        ),
        spacer(0.2),
    ]
    elems += ss("ss5b_email_lookup_by_lastname_n_dept.png",
                caption="SS5b — Email retrieved by last name and department number.")
    elems += [
        spacer(0.4),
        h2("6.4 Phone Lookup by Name — Screenshot 6"),
        p(
            "Option 4 sends <font name='Courier'>{\"action\": \"phone_by_name\", ...}</font>. "
            "The same JSON structure as the email lookup but with a different action field, "
            "demonstrating how one protocol format can dispatch to multiple server behaviours."
        ),
        spacer(0.2),
    ]
    elems += ss("ss6_phone_lookup_by_names.png",
                caption="SS6 — Phone number retrieved by providing first and last name.")
    elems += [
        spacer(0.4),
        h2("6.5 List All Members in a Department — Screenshot 7"),
        p(
            "Option 5 sends <font name='Courier'>{\"action\": \"list_by_dept\", \"dept_no\": N}</font>. "
            "The client only needs to supply a department number; the server returns a formatted "
            "table of every person in that department."
        ),
        spacer(0.2),
    ]
    elems += ss("ss7_list_by_department.png",
                caption="SS7 — All members of a selected department returned by the server.")
    elems += [
        spacer(0.4),
        h2("6.6 Server Protocol Help — Screenshot 8"),
        p(
            "Option 7 sends <font name='Courier'>{\"action\": \"help\"}</font> and receives the "
            "full protocol reference document. This is a real-world pattern: a self-describing "
            "protocol that documents itself at runtime so any client can discover what actions "
            "are available without reading source code."
        ),
        spacer(0.2),
    ]
    elems += ss("ss8_server_help.png",
                caption="SS8 — The server's built-in protocol reference returned over the socket.")
    elems += [spacer()]
    return elems

# ── Section 7: Error Handling ─────────────────────────────────────────────────
def section_errors():
    elems = [
        h1("7. Error Handling"),
        hr(),
        p(
            "Robust socket applications must handle errors at two levels: "
            "<b>application-level errors</b> (e.g., a lookup that finds no match) and "
            "<b>network-level errors</b> (e.g., the server disappears while the client is running)."
        ),
        spacer(0.2),
        h2("7.1 Record Not Found — Screenshot 9"),
        p(
            "When a query finds no matching record, the server sends back a plain-text error "
            "string beginning with <font name='Courier'>ERROR:</font>. The response travels "
            "over the same socket connection using the same sentinel-terminated protocol — "
            "errors are just another type of response."
        ),
        spacer(0.2),
    ]
    elems += ss("ss9_no_record_found.png",
                caption="SS9 — The server returns an ERROR message when no matching record exists.")
    elems += [
        spacer(0.4),
        h2("7.2 Connection Refused — Screenshot 10"),
        p(
            "If the client tries to connect while the server is not running, "
            "<font name='Courier'>sock.connect()</font> raises "
            "<font name='Courier'>ConnectionRefusedError</font> (or "
            "<font name='Courier'>OSError</font> on timeout). The client catches this and "
            "prints a clear message rather than crashing with a raw traceback."
        ),
        spacer(0.2),
    ]
    elems += ss("ss10_connection_refused.png",
                caption="SS10 — Client reports connection refused when the server is not running.")
    elems += [spacer()]
    return elems

# ── Section 8: Concurrent Clients (Threading) ────────────────────────────────
def section_threading():
    elems = [
        h1("8. Handling Multiple Clients — Threading"),
        hr(),
        p(
            "One of the lab requirements is that the server must accept several client connections "
            "at a time. A naive server that handles one client at a time inside the accept loop "
            "would block all other clients until the first one disconnects."
        ),
        p(
            "Our server solves this with <b>threading</b>: every time "
            "<font name='Courier'>accept()</font> returns a new connection, a dedicated thread "
            "is spawned to handle that client independently. The main thread immediately returns "
            "to waiting for the next connection."
        ),
        code(
            'while True:\n'
            '    conn, addr = srv.accept()\n'
            '    t = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)\n'
            '    t.start()'
        ),
        p(
            "The <font name='Courier'>daemon=True</font> flag means the threads are automatically "
            "killed when the main program exits, so the server shuts down cleanly on Ctrl+C."
        ),
        spacer(0.2),
        h2("8.1 Two Clients Connected Simultaneously — Screenshot 11"),
        p(
            "The screenshot below shows the server terminal with two separate clients connected "
            "at the same time. Each client has a different ephemeral port number, confirming they "
            "are distinct TCP connections being served by separate threads."
        ),
        spacer(0.2),
    ]
    elems += ss("ss11_threading.png",
                caption="SS11 — Server logs two simultaneous connections, each handled by its own thread.")
    elems += [
        spacer(0.4),
        h2("8.2 Client Disconnect Logged on the Server — Screenshot 12"),
        p(
            "When a client exits (option 0), the TCP connection is closed. The server's "
            "<font name='Courier'>client_handler</font> detects this because "
            "<font name='Courier'>recv()</font> returns empty bytes, the thread ends, "
            "and the disconnect is logged. This demonstrates the full lifecycle of a socket: "
            "<i>connect → exchange data → close</i>."
        ),
        spacer(0.2),
    ]
    elems += ss("ss12_disconnection_logged.png",
                caption="SS12 — Server logs '[-] Disconnected' when a client closes the connection.")
    elems += [spacer()]
    return elems

# ── Section 9: Summary ────────────────────────────────────────────────────────
def section_summary():
    elems = [
        h1("9. Summary"),
        hr(),
        p(
            "This lab demonstrated the complete lifecycle of a TCP socket-based "
            "client-server application using Python. The key concepts covered are:"
        ),
        spacer(0.1),
    ]

    rows = [
        ["Concept",           "Where demonstrated"],
        ["socket() / SOCK_STREAM",     "server.py:264, client.py:138"],
        ["bind() + listen()",          "server.py:265-267 — server binds to 0.0.0.0:9090"],
        ["connect()",                  "client.py:136 — client dials the server"],
        ["accept()",                   "server.py:269 — server blocks until a client arrives"],
        ["sendall() / recv()",         "client.py:34,38 — full send + chunked receive loop"],
        ["Message framing (sentinel)", "<<END>> token marks end of every server response"],
        ["JSON application protocol",  "All requests are JSON; responses are plain text"],
        ["Threading",                  "server.py:271 — one thread per connected client"],
        ["Error handling",             "SS9 (not found), SS10 (refused), SS12 (disconnect)"],
    ]

    col_widths = [6.5*cm, 10*cm]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  UR_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9.5),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#AAAAAA")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
    ]))
    elems.append(tbl)
    elems += [
        spacer(0.5),
        p(
            "Through building and running this application, we saw that socket programming "
            "requires careful attention to <b>framing</b> (knowing where messages begin and end), "
            "<b>concurrency</b> (serving multiple clients without blocking), and "
            "<b>error handling</b> at both the network and application layer. "
            "These are the same principles that underpin every distributed system, "
            "from web servers to database clusters."
        ),
    ]
    return elems

# ── Build the PDF ─────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title="Introduction to Socket Programming",
        author="UR-CST Department of Computer Science",
    )

    story = []
    story += cover_page()
    story += section_introduction()
    story += section_lab_overview()
    story += section_server()
    story += section_client()
    story += section_protocol()
    story += section_queries()
    story += section_errors()
    story += section_threading()
    story += section_summary()

    doc.build(story)
    print(f"Report written to: {OUTPUT_PATH}")

if __name__ == "__main__":
    build()
