"""
DOCX report generator for the Socket Programming lab assignment.
Run:  python generate_report_docx.py
Output: report.docx in the same directory.
"""

import os
from datetime import date
from PIL import Image as PILImage

from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS  = os.path.join(BASE_DIR, "screenshots")
OUTPUT_PATH  = os.path.join(BASE_DIR, "report.docx")
UR_LOGO      = os.path.join(SCREENSHOTS, "ur_logo.png")

TODAY = date.today().strftime("%B %d, %Y")

# ── Colours ───────────────────────────────────────────────────────────────────
UR_BLUE  = RGBColor(0x00, 0x30, 0x87)
UR_GOLD  = RGBColor(0xF5, 0xA8, 0x00)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
GREY     = RGBColor(0x55, 0x55, 0x55)
LIGHT_BG = RGBColor(0xF2, 0xF6, 0xFC)
CODE_BG  = RGBColor(0x1E, 0x1E, 0x2E)
CODE_FG  = RGBColor(0xCD, 0xD6, 0xF4)

# Page content width in inches (A4 minus 2.2cm margins each side)
CONTENT_W = Inches(8.27) - 2 * Cm(2.2)
MAX_IMG_H = Inches(4.5)

# ── XML helpers ───────────────────────────────────────────────────────────────
def set_cell_bg(cell, rgb: RGBColor):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    hex_color = f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)

def set_table_borders(table):
    tbl   = table._tbl
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"),   "single")
        el.set(qn("w:sz"),    "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "AAAAAA")
        borders.append(el)
    tblPr.append(borders)

def add_run_font(run, bold=False, italic=False, size=None,
                 color=None, font_name="Calibri", bg=None):
    run.bold   = bold
    run.italic = italic
    run.font.name = font_name
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    if bg:
        rPr = run._r.get_or_add_rPr()
        shd = OxmlElement("w:shd")
        hex_bg = f"{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}"
        shd.set(qn("w:val"),   "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"),  hex_bg)
        rPr.append(shd)

def page_break(doc):
    doc.add_page_break()

# ── Style helpers ─────────────────────────────────────────────────────────────
def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    size = 15 if level == 1 else 12
    add_run_font(run, bold=True, size=size, color=UR_BLUE)
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after  = Pt(4)
    # Blue bottom border for level-1 headings
    if level == 1:
        pPr  = p._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        bot  = OxmlElement("w:bottom")
        bot.set(qn("w:val"),   "single")
        bot.set(qn("w:sz"),    "6")
        bot.set(qn("w:space"), "1")
        bot.set(qn("w:color"), "F5A800")
        pBdr.append(bot)
        pPr.append(pBdr)
    return p

def add_body(doc, text, italic=False, space_after=6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    add_run_font(run, italic=italic, size=10.5)
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    add_run_font(run, size=10.5)
    p.paragraph_format.space_after = Pt(3)
    return p

def add_code(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    add_run_font(run, font_name="Courier New", size=9, color=CODE_FG, bg=CODE_BG)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.left_indent  = Cm(0.8)
    return p

def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    add_run_font(run, italic=True, size=9, color=GREY)
    p.paragraph_format.space_after = Pt(10)
    return p

def add_spacer(doc, size_pt=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(size_pt)
    run = p.add_run("")
    run.font.size = Pt(1)

# ── Image helper ──────────────────────────────────────────────────────────────
def add_screenshot(doc, filename, caption=None):
    path = os.path.join(SCREENSHOTS, filename)
    if not os.path.exists(path):
        add_caption(doc, f"[Missing screenshot: {filename}]")
        return

    pil  = PILImage.open(path)
    ow, oh = pil.size
    aspect = oh / ow

    target_w = CONTENT_W
    target_h = target_w * aspect

    if target_h > MAX_IMG_H:
        target_h = MAX_IMG_H
        target_w = target_h / aspect

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(path, width=target_w, height=target_h)

    if caption:
        add_caption(doc, caption)

# ── Cover page ────────────────────────────────────────────────────────────────
def cover_page(doc):
    # Logo
    if os.path.exists(UR_LOGO):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(20)
        run = p.add_run()
        run.add_picture(UR_LOGO, width=Cm(4), height=Cm(4))

    add_spacer(doc, 10)

    # Institution lines
    for line in [
        "UNIVERSITY OF RWANDA",
        "COLLEGE OF SCIENCE AND TECHNOLOGY",
        "SCHOOL OF ICT",
        "DEPARTMENT OF COMPUTER SCIENCE",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(line)
        add_run_font(run, bold=True, size=13, color=UR_BLUE)
        p.paragraph_format.space_after = Pt(2)

    add_spacer(doc, 14)

    # Course label
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Parallel and Distributed Computing")
    add_run_font(run, size=12, color=GREY)
    p.paragraph_format.space_after = Pt(6)

    # Assignment title
    for line in [
        "Distributed Systems Assignment Lab:",
        "Introduction to Socket Programming",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(line)
        add_run_font(run, bold=True, size=16, color=UR_BLUE)
        p.paragraph_format.space_after = Pt(4)

    add_spacer(doc, 16)

    # Members table heading
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Group Members Participation Table")
    add_run_font(run, size=12, color=GREY)
    p.paragraph_format.space_after = Pt(6)

    # Members table
    members = [
        ("Row No.", "Registration No.", "Names"),
        ("1",  "222004611", "Clement MUGISHA"),
        ("2",  "222014353", "Marie Mireille Irafasha"),
        ("3",  "222005615", "Joseph Bonheur Iradukunda"),
        ("4",  "222002123", "Rose Umutesi"),
        ("5",  "222019837", "Izere Bugingo Vainqueur Beryl"),
        ("6",  "222002227", "Elvis Mugisha"),
        ("7",  "222005152", "Uwineza Florance"),
        ("8",  "222018513", "Mugisha Edson"),
        ("9",  "222004590", "Sugira Herve"),
        ("10", "222008836", "Marie Claire Nisingizwe"),
        ("11", "___________", "___________________________"),
    ]

    tbl = doc.add_table(rows=len(members), cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Cm(2), Cm(5), Cm(9)]
    for i, row in enumerate(tbl.rows):
        for j, (cell, text) in enumerate(zip(row.cells, members[i])):
            cell.width = col_widths[j]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cp = cell.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER if j < 2 else WD_ALIGN_PARAGRAPH.LEFT
            run = cp.add_run(text)
            if i == 0:
                add_run_font(run, bold=True, size=10, color=WHITE)
                set_cell_bg(cell, UR_BLUE)
            else:
                add_run_font(run, size=9.5)
                if i % 2 == 0:
                    set_cell_bg(cell, LIGHT_BG)
    set_table_borders(tbl)

    add_spacer(doc, 20)

    # Date
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(TODAY)
    add_run_font(run, italic=True, size=11, color=GREY)

    page_break(doc)

# ── Section 1: Introduction ───────────────────────────────────────────────────
def section_introduction(doc):
    add_heading(doc, "1. What is Socket Programming?")
    add_body(doc,
        "A socket is one endpoint of a two-way communication link between two programs "
        "running on a network. A socket is bound to a port number so that the transport layer "
        "can identify the application to which data is destined. Sockets are the fundamental "
        "building blocks of network communication — they allow processes on different machines "
        "(or the same machine) to exchange data as if they were writing to and reading from a file."
    )
    add_body(doc,
        "Socket programming is the practice of writing programs that use sockets to communicate "
        "over a network. Python exposes this through the built-in socket module, which provides "
        "a low-level interface directly to the operating system's networking stack."
    )
    add_heading(doc, "1.1 TCP vs UDP", level=2)
    add_body(doc,
        "There are two dominant transport-layer protocols used with sockets:"
    )
    add_bullet(doc,
        "TCP (Transmission Control Protocol) — connection-oriented, reliable, ordered, and "
        "error-checked. Before any data is exchanged a connection is established through a "
        "three-way handshake (SYN → SYN-ACK → ACK). Every byte sent is guaranteed to arrive "
        "in the correct order. This makes TCP ideal for applications where data integrity matters, "
        "such as our directory lookup service."
    )
    add_bullet(doc,
        "UDP (User Datagram Protocol) — connectionless, unreliable, and unordered. Packets "
        "are fired without establishing a connection and may arrive out of order or not at all. "
        "UDP is preferred when speed matters more than reliability, such as video streaming or "
        "online games."
    )
    add_body(doc, "This lab uses TCP sockets exclusively, matching Python's socket.SOCK_STREAM type.")

    add_heading(doc, "1.2 The Client-Server Model", level=2)
    add_body(doc, "Socket-based applications almost always follow the client-server model:")
    add_bullet(doc,
        "The server is a long-running process that binds to a fixed address and port, "
        "listens for incoming connections, and serves requests."
    )
    add_bullet(doc,
        "The client is a shorter-lived process that knows the server's address and port, "
        "initiates the connection, sends requests, and reads responses."
    )
    add_body(doc,
        "In our lab, server/server.py is the server and client/client.py is the client. "
        "The server holds a database of UR-CST students and staff. Clients connect and "
        "query that database over TCP."
    )

# ── Section 2: Lab Overview ───────────────────────────────────────────────────
def section_lab_overview(doc):
    add_heading(doc, "2. Lab Overview — UR-CST Staff/Student Directory")
    add_body(doc,
        "The School of ICT at the University of Rwanda — College of Science and Technology "
        "(UR-CST) has four departments sharing a central server:"
    )
    for dept in [
        "Department of Computer Engineering",
        "Department of Computer Science",
        "Department of Information Systems",
        "Department of Information Technology",
    ]:
        add_bullet(doc, dept)

    add_body(doc,
        "The central server stores records for every student and employee. Each record contains: "
        "department number, first name, last name, phone number, and email address. "
        "Any client (student or teacher) can connect to the server and make one of the following queries:"
    )
    add_bullet(doc, "List all records — retrieve the full directory.")
    add_bullet(doc, "Email by first name + last name — look up a person's email directly.")
    add_bullet(doc, "Email by last name + department number — useful when only partial information is known.")
    add_bullet(doc, "Phone by first name + last name — retrieve a phone number.")
    add_bullet(doc, "List all members in a department — retrieve everyone in a given department.")

# ── Section 3: Server ─────────────────────────────────────────────────────────
def section_server(doc):
    add_heading(doc, "3. The Server — Binding, Listening, and Accepting Connections")
    add_body(doc,
        "The server side of a TCP socket application goes through four distinct steps before "
        "it can serve any client: create, bind, listen, and accept."
    )
    add_heading(doc, "3.1 Creating and Binding the Socket", level=2)
    add_body(doc,
        "The server creates a TCP socket, sets the SO_REUSEADDR option so the port can be "
        "reused immediately after a restart, then binds to 0.0.0.0:9090. Binding to 0.0.0.0 "
        "means the server listens on all available network interfaces."
    )
    add_code(doc,
        "srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n"
        'srv.bind(("0.0.0.0", 9090))\n'
        "srv.listen(10)"
    )
    add_heading(doc, "3.2 Server Startup — Screenshot 1", level=2)
    add_body(doc,
        "Running python server/server.py produces the following startup output, confirming "
        "the socket is bound and listening:"
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss1_server_startup_output.png",
        "SS1 — Server starts, binds to 0.0.0.0:9090, and enters the listening state.")

    add_heading(doc, "3.3 Accepting Connections", level=2)
    add_body(doc,
        "srv.listen(10) sets the backlog — the maximum number of queued connections waiting "
        "to be accepted. The server then loops forever, calling srv.accept(), which blocks "
        "until a client connects and returns a new socket object dedicated to that client "
        "along with the client's address."
    )
    add_code(doc,
        "while True:\n"
        "    conn, addr = srv.accept()\n"
        "    t = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)\n"
        "    t.start()"
    )

# ── Section 4: Client ─────────────────────────────────────────────────────────
def section_client(doc):
    add_heading(doc, "4. The Client — Connecting to the Server")
    add_body(doc,
        "The client creates the same type of TCP socket and calls connect() with the server's "
        "IP address and port. This triggers the TCP three-way handshake. A 5-second timeout "
        "is set before connecting so the client fails fast if the server is unreachable."
    )
    add_code(doc,
        "sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "sock.settimeout(5)\n"
        'sock.connect(("127.0.0.1", 9090))\n'
        "sock.settimeout(None)   # restore blocking mode after connect"
    )
    add_heading(doc, "4.1 The Connection Moment — Screenshot 2", level=2)
    add_body(doc,
        "The screenshot below shows both terminals side by side at the instant a client "
        "connects. The server terminal (left) logs the client's address. The client terminal "
        "(right) confirms the connection and displays the menu."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss2_both_terminals_at_client_connection.png",
        "SS2 — Left: server logs '[+] Connected'. Right: client prints 'Connected.' and shows the menu.")

    add_heading(doc, "4.2 The Client Menu — Screenshot 3", level=2)
    add_body(doc,
        "Once connected, the client presents a menu of all supported query types. "
        "Each option maps to a different JSON action sent to the server."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss3_client_menu.png",
        "SS3 — The client menu listing all available query options (0–7).")

# ── Section 5: Protocol ───────────────────────────────────────────────────────
def section_protocol(doc):
    add_heading(doc, "5. The Application Protocol — JSON over TCP")
    add_body(doc,
        "Raw TCP is just a stream of bytes — it has no concept of messages or boundaries. "
        "Our application defines its own protocol on top of TCP:"
    )
    add_bullet(doc, "Requests are newline-terminated JSON objects sent by the client.")
    add_bullet(doc,
        "Responses are plain-text strings sent by the server, terminated by the special "
        "sentinel token <<END>>."
    )
    add_body(doc,
        "The sentinel pattern is necessary because TCP is a stream protocol — the receiver "
        "does not know where one message ends and the next begins. By agreeing on a terminator, "
        "both sides know exactly when a full response has arrived."
    )
    add_heading(doc, "5.1 Sending a Request", level=2)
    add_code(doc,
        'payload = {"action": "email_by_name", "first_name": "Jean", "last_name": "Mugisha"}\n'
        'message = json.dumps(payload) + "\\n"\n'
        "sock.sendall(message.encode(\"utf-8\"))"
    )
    add_heading(doc, "5.2 Receiving a Response", level=2)
    add_body(doc,
        "recv() may return less than the full response in a single call — TCP can split data "
        "across multiple packets. The client loops, accumulating chunks, until it sees the sentinel:"
    )
    add_code(doc,
        'response = b""\n'
        "while True:\n"
        "    chunk = sock.recv(4096)\n"
        "    if not chunk:\n"
        '        raise ConnectionResetError("Server closed the connection unexpectedly.")\n'
        "    response += chunk\n"
        '    if b"<<END>>" in response:\n'
        "        break"
    )

# ── Section 6: Queries ────────────────────────────────────────────────────────
def section_queries(doc):
    add_heading(doc, "6. Queries in Action")

    add_heading(doc, "6.1 List All Records — Screenshot 4", level=2)
    add_body(doc,
        'Option 1 sends {"action": "list_all"}. The server iterates over every record in the '
        "database and returns a formatted table. This is the largest payload and best illustrates "
        "the recv-loop: the response spans multiple TCP segments before the sentinel arrives."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss4_list_all_records.png",
        "SS4 — Full directory table returned by the server for the 'list_all' action.")

    add_heading(doc, "6.2 Email Lookup by First Name + Last Name — Screenshot 5a", level=2)
    add_body(doc,
        'Option 2 sends {"action": "email_by_name", "first_name": "...", "last_name": "..."}. '
        "The server searches the database and returns a single email address — a minimal but "
        "complete request-response cycle."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss5a_email_lookup_by_first_n_last_name.png",
        "SS5a — Email retrieved by providing first and last name.")

    add_heading(doc, "6.3 Email Lookup by Last Name + Department — Screenshot 5b", level=2)
    add_body(doc,
        'Option 3 sends {"action": "email_by_lastname_dept", "last_name": "...", "dept_no": N}. '
        "This is the second email-lookup method specified in the lab requirements — useful when "
        "only partial information is known. The dept_no field shows how integer parameters are "
        "carried inside the JSON."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss5b_email_lookup_by_lastname_n_dept.png",
        "SS5b — Email retrieved by last name and department number.")

    add_heading(doc, "6.4 Phone Lookup by Name — Screenshot 6", level=2)
    add_body(doc,
        'Option 4 sends {"action": "phone_by_name", ...}. The same JSON structure as the email '
        "lookup but with a different action field, demonstrating how one protocol format can "
        "dispatch to multiple server behaviours."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss6_phone_lookup_by_names.png",
        "SS6 — Phone number retrieved by providing first and last name.")

    add_heading(doc, "6.5 List All Members in a Department — Screenshot 7", level=2)
    add_body(doc,
        'Option 5 sends {"action": "list_by_dept", "dept_no": N}. The client only needs to '
        "supply a department number; the server returns a formatted table of every person in "
        "that department."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss7_list_by_department.png",
        "SS7 — All members of a selected department returned by the server.")

    add_heading(doc, "6.6 Server Protocol Help — Screenshot 8", level=2)
    add_body(doc,
        'Option 7 sends {"action": "help"} and receives the full protocol reference document. '
        "This is a real-world pattern: a self-describing protocol that documents itself at "
        "runtime so any client can discover what actions are available without reading source code."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss8_server_help.png",
        "SS8 — The server's built-in protocol reference returned over the socket.")

# ── Section 7: Error Handling ─────────────────────────────────────────────────
def section_errors(doc):
    add_heading(doc, "7. Error Handling")
    add_body(doc,
        "Robust socket applications must handle errors at two levels: application-level errors "
        "(e.g., a lookup that finds no match) and network-level errors (e.g., the server "
        "disappears while the client is running)."
    )

    add_heading(doc, "7.1 Record Not Found — Screenshot 9", level=2)
    add_body(doc,
        "When a query finds no matching record, the server sends back a plain-text error string "
        "beginning with ERROR:. The response travels over the same socket connection using the "
        "same sentinel-terminated protocol — errors are just another type of response."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss9_no_record_found.png",
        "SS9 — The server returns an ERROR message when no matching record exists.")

    add_heading(doc, "7.2 Connection Refused — Screenshot 10", level=2)
    add_body(doc,
        "If the client tries to connect while the server is not running, sock.connect() raises "
        "ConnectionRefusedError (or OSError on timeout). The client catches this and prints a "
        "clear message rather than crashing with a raw traceback."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss10_connection_refused.png",
        "SS10 — Client reports connection refused when the server is not running.")

# ── Section 8: Threading ──────────────────────────────────────────────────────
def section_threading(doc):
    add_heading(doc, "8. Handling Multiple Clients — Threading")
    add_body(doc,
        "One of the lab requirements is that the server must accept several client connections "
        "at a time. A naive server that handles one client at a time inside the accept loop "
        "would block all other clients until the first one disconnects."
    )
    add_body(doc,
        "Our server solves this with threading: every time accept() returns a new connection, "
        "a dedicated thread is spawned to handle that client independently. The main thread "
        "immediately returns to waiting for the next connection."
    )
    add_code(doc,
        "while True:\n"
        "    conn, addr = srv.accept()\n"
        "    t = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)\n"
        "    t.start()"
    )
    add_body(doc,
        "The daemon=True flag means the threads are automatically killed when the main program "
        "exits, so the server shuts down cleanly on Ctrl+C."
    )

    add_heading(doc, "8.1 Two Clients Connected Simultaneously — Screenshot 11", level=2)
    add_body(doc,
        "The screenshot below shows the server terminal with two separate clients connected at "
        "the same time. Each client has a different ephemeral port number, confirming they are "
        "distinct TCP connections being served by separate threads."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss11_threading.png",
        "SS11 — Server logs two simultaneous connections, each handled by its own thread.")

    add_heading(doc, "8.2 Client Disconnect Logged on the Server — Screenshot 12", level=2)
    add_body(doc,
        "When a client exits (option 0), the TCP connection is closed. The server's "
        "client_handler detects this because recv() returns empty bytes, the thread ends, "
        "and the disconnect is logged. This demonstrates the full lifecycle of a socket: "
        "connect → exchange data → close."
    )
    add_spacer(doc, 4)
    add_screenshot(doc, "ss12_disconnection_logged.png",
        "SS12 — Server logs '[-] Disconnected' when a client closes the connection.")

# ── Section 9: Summary ────────────────────────────────────────────────────────
def section_summary(doc):
    add_heading(doc, "9. Summary")
    add_body(doc,
        "This lab demonstrated the complete lifecycle of a TCP socket-based client-server "
        "application using Python. The key concepts covered are:"
    )
    add_spacer(doc, 4)

    rows = [
        ("Concept",                      "Where demonstrated"),
        ("socket() / SOCK_STREAM",       "server.py:264, client.py:138"),
        ("bind() + listen()",            "server.py:265-267 — server binds to 0.0.0.0:9090"),
        ("connect()",                    "client.py:136 — client dials the server"),
        ("accept()",                     "server.py:269 — server blocks until a client arrives"),
        ("sendall() / recv()",           "client.py:34,38 — full send + chunked receive loop"),
        ("Message framing (sentinel)",   "<<END>> token marks end of every server response"),
        ("JSON application protocol",    "All requests are JSON; responses are plain text"),
        ("Threading",                    "server.py:271 — one thread per connected client"),
        ("Error handling",               "SS9 (not found), SS10 (refused), SS12 (disconnect)"),
    ]

    tbl = doc.add_table(rows=len(rows), cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Cm(7), Cm(10.5)]

    for i, (concept, demo) in enumerate(rows):
        row = tbl.rows[i]
        for j, (cell, text) in enumerate(zip(row.cells, (concept, demo))):
            cell.width = col_widths[j]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cp = cell.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = cp.add_run(text)
            if i == 0:
                add_run_font(run, bold=True, size=10, color=WHITE)
                set_cell_bg(cell, UR_BLUE)
            else:
                add_run_font(run, size=9.5)
                if i % 2 == 0:
                    set_cell_bg(cell, LIGHT_BG)
    set_table_borders(tbl)

    add_spacer(doc, 12)
    add_body(doc,
        "Through building and running this application, we saw that socket programming requires "
        "careful attention to framing (knowing where messages begin and end), concurrency "
        "(serving multiple clients without blocking), and error handling at both the network "
        "and application layer. These are the same principles that underpin every distributed "
        "system, from web servers to database clusters."
    )

# ── Build the document ────────────────────────────────────────────────────────
def build():
    doc = Document()

    # Page size: A4
    section = doc.sections[0]
    section.page_width  = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = section.right_margin = Cm(2.2)
    section.top_margin  = section.bottom_margin = Cm(2.2)

    cover_page(doc)
    section_introduction(doc)
    section_lab_overview(doc)
    section_server(doc)
    section_client(doc)
    section_protocol(doc)
    section_queries(doc)
    section_errors(doc)
    section_threading(doc)
    section_summary(doc)

    doc.save(OUTPUT_PATH)
    print(f"Report written to: {OUTPUT_PATH}")

if __name__ == "__main__":
    build()
