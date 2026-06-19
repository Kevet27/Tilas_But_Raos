import streamlit as st
import sqlite3
import hashlib
import os

# ================= CONFIG =================

st.set_page_config(
    page_title="TILAS BUT RAOS",
    layout="wide"
)

# ================= FOLDER GAMBAR =================

if not os.path.exists("gambar_produk"):
    os.makedirs("gambar_produk")

# ================= DATABASE =================

conn = sqlite3.connect(
    "tilas_raos.db",
    check_same_thread=False
)

c = conn.cursor()

# ================= TABEL =================

c.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS produk(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nama TEXT,
harga INTEGER,
gambar TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS keranjang(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
produk TEXT,
harga INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS pesanan(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
alamat TEXT,
pembayaran TEXT,
total INTEGER
)
""")

conn.commit()

# ================= SESSION =================

if "login" not in st.session_state:
    st.session_state.login = False

if "user" not in st.session_state:
    st.session_state.user = ""

# ================= HASH PASSWORD =================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# ================= LOGIN =================

def login_page():

    st.title("👕 TILAS BUT RAOS")

    menu = st.selectbox(
        "Menu",
        ["Login","Register"]
    )

    if menu == "Register":

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Daftar"):

            try:

                c.execute(
                """
                INSERT INTO users
                (username,password)
                VALUES(?,?)
                """,
                (
                    username,
                    hash_password(password)
                )
                )

                conn.commit()

                st.success(
                    "Akun berhasil dibuat"
                )

            except:

                st.error(
                    "Username sudah digunakan"
                )

    else:

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            c.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            AND password=?
            """,
            (
                username,
                hash_password(password)
            )
            )

            data = c.fetchone()

            if data:

                st.session_state.login = True
                st.session_state.user = username

                st.rerun()

            else:

                st.error(
                    "Username atau password salah"
                )

# ================= BERANDA =================

def home():

    st.title("🏠 Beranda")

    data = c.execute(
        "SELECT * FROM produk"
    ).fetchall()

    if len(data) == 0:

        st.info(
            "Belum ada produk"
        )

    else:

        col = st.columns(3)

        nomor = 0

        for p in data:

            with col[nomor % 3]:

                if p[3] != "":

                    try:

                        st.image(
                            "gambar_produk/" + p[3],
                            use_container_width=True
                        )

                    except:
                        pass

                st.subheader(
                    p[1]
                )

                st.write(
                    "Rp",
                    format(
                        p[2],
                        ","
                    )
                )

                if st.button(
                    "Tambah Keranjang",
                    key="produk"+str(p[0])
                ):

                    c.execute(
                    """
                    INSERT INTO keranjang
                    (user,produk,harga)
                    VALUES(?,?,?)
                    """,
                    (
                        st.session_state.user,
                        p[1],
                        p[2]
                    )
                    )

                    conn.commit()

                    st.success(
                        "Produk ditambahkan"
                    )

            nomor += 1


# ================= KERANJANG =================

def cart():

    st.title("🛒 Keranjang")

    data = c.execute(
    """
    SELECT *
    FROM keranjang
    WHERE user=?
    """,
    (
        st.session_state.user,
    )
    ).fetchall()

    total = 0

    if len(data) == 0:

        st.info(
            "Keranjang kosong"
        )

    else:

        for x in data:

            col1, col2 = st.columns([4,1])

            with col1:

                st.write(
                    x[2],
                    "- Rp",
                    format(
                        x[3],
                        ","
                    )
                )

            with col2:

                if st.button(
                    "Hapus",
                    key="hapus"+str(x[0])
                ):

                    c.execute(
                    """
                    DELETE FROM keranjang
                    WHERE id=?
                    """,
                    (
                        x[0],
                    )
                    )

                    conn.commit()

                    st.rerun()

            total += x[3]

        st.subheader(
            "Total : Rp "
            +
            format(
                total,
                ","
            )
        )


# ================= CHECKOUT =================

def checkout():

    st.title("📦 Checkout")

    total = 0

    data = c.execute(
    """
    SELECT harga
    FROM keranjang
    WHERE user=?
    """,
    (
        st.session_state.user,
    )
    ).fetchall()

    for x in data:

        total += x[0]

    st.subheader(
        "Total Belanja : Rp "
        +
        format(
            total,
            ","
        )
    )

    alamat = st.text_area(
        "Alamat Lengkap"
    )

    pembayaran = st.selectbox(
        "Metode Pembayaran",
        [
            "Transfer Bank",
            "DANA",
            "OVO"
        ]
    )

    if st.button(
        "Bayar"
    ):

        c.execute(
        """
        INSERT INTO pesanan
        (user,alamat,pembayaran,total)
        VALUES(?,?,?,?)
        """,
        (
            st.session_state.user,
            alamat,
            pembayaran,
            total
        )
        )

        conn.commit()

        c.execute(
        """
        DELETE FROM keranjang
        WHERE user=?
        """,
        (
            st.session_state.user,
        )
        )

        conn.commit()

        st.success(
            "Pesanan berhasil dibuat"
        )


# ================= RIWAYAT PESANAN =================

def riwayat():

    st.title(
        "📋 Riwayat Pesanan"
    )

    data = c.execute(
    """
    SELECT *
    FROM pesanan
    WHERE user=?
    """,
    (
        st.session_state.user,
    )
    ).fetchall()

    if len(data) == 0:

        st.info(
            "Belum ada pesanan"
        )

    else:

        for x in data:

            st.write(
                "Alamat :",
                x[2]
            )

            st.write(
                "Pembayaran :",
                x[3]
            )

            st.write(
                "Total : Rp",
                format(
                    x[4],
                    ","
                )
            )

            st.divider()
# ================= ADMIN PRODUK =================

def admin_produk():

    st.title("⚙️ Admin Produk")

    tab1, tab2 = st.tabs(
        ["Tambah Produk", "Kelola Produk"]
    )

    # ================= TAMBAH PRODUK =================

    with tab1:

        nama = st.text_input(
            "Nama Produk"
        )

        harga = st.number_input(
            "Harga",
            min_value=1000,
            step=1000
        )

        gambar = st.file_uploader(
            "Upload Foto Produk",
            type=["jpg","jpeg","png"]
        )

        if st.button(
            "Tambah Produk"
        ):

            nama_file = ""

            if gambar is not None:

                nama_file = gambar.name

                with open(
                    os.path.join(
                        "gambar_produk",
                        nama_file
                    ),
                    "wb"
                ) as f:

                    f.write(
                        gambar.getbuffer()
                    )

            c.execute(
            """
            INSERT INTO produk
            (nama,harga,gambar)
            VALUES(?,?,?)
            """,
            (
                nama,
                int(harga),
                nama_file
            )
            )

            conn.commit()

            st.success(
                "Produk berhasil ditambahkan"
            )

            st.rerun()

    # ================= KELOLA PRODUK =================

    with tab2:

        data = c.execute(
        """
        SELECT *
        FROM produk
        """
        ).fetchall()

        if len(data) == 0:

            st.info(
                "Belum ada produk"
            )

        else:

            for p in data:

                st.divider()

                col1, col2 = st.columns([1,2])

                with col1:

                    if p[3] != "":

                        try:

                            st.image(
                                "gambar_produk/" + p[3],
                                width=150
                            )

                        except:
                            pass

                with col2:

                    nama_baru = st.text_input(
                        "Nama Produk",
                        value=p[1],
                        key="nama"+str(p[0])
                    )

                    harga_baru = st.number_input(
                        "Harga",
                        value=int(p[2]),
                        key="harga"+str(p[0])
                    )

                    gambar_baru = st.file_uploader(
                        "Ganti Foto",
                        type=["jpg","jpeg","png"],
                        key="gambar"+str(p[0])
                    )

                    col_update, col_hapus = st.columns(2)

                    with col_update:

                        if st.button(
                            "Update",
                            key="update"+str(p[0])
                        ):

                            nama_file = p[3]

                            if gambar_baru is not None:

                                nama_file = gambar_baru.name

                                with open(
                                    os.path.join(
                                        "gambar_produk",
                                        nama_file
                                    ),
                                    "wb"
                                ) as f:

                                    f.write(
                                        gambar_baru.getbuffer()
                                    )

                            c.execute(
                            """
                            UPDATE produk
                            SET nama=?,
                            harga=?,
                            gambar=?
                            WHERE id=?
                            """,
                            (
                                nama_baru,
                                int(harga_baru),
                                nama_file,
                                p[0]
                            )
                            )

                            conn.commit()

                            st.success(
                                "Produk berhasil diperbarui"
                            )

                            st.rerun()

                    with col_hapus:

                        if st.button(
                            "Hapus",
                            key="hapus"+str(p[0])
                        ):

                            c.execute(
                            """
                            DELETE FROM produk
                            WHERE id=?
                            """,
                            (
                                p[0],
                            )
                            )

                            conn.commit()

                            st.rerun()


# ================= MENU UTAMA =================

if not st.session_state.login:

    login_page()

else:

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Beranda",
            "Keranjang",
            "Checkout",
            "Riwayat Pesanan",
            "Admin",
            "Logout"
        ]
    )

    if menu == "Beranda":

        home()

    elif menu == "Keranjang":

        cart()

    elif menu == "Checkout":

        checkout()

    elif menu == "Riwayat Pesanan":

        riwayat()

    elif menu == "Admin":

        st.title("⚙️ Admin")

        password_admin = st.text_input(
            "Masukkan Password Admin",
            type="password"
        )

        if password_admin == "admin123":

            admin_produk()

        elif password_admin != "":

            st.error(
                "Password admin salah"
            )

    elif menu == "Logout":

        st.session_state.login = False
        st.session_state.user = ""

        st.rerun()
