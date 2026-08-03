import customtkinter as ctk
from customtkinter import CTkInputDialog
from tkinter import filedialog, messagebox
import pymysql

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class DialogoNuevaColumna(ctk.CTkToplevel):
    def __init__(self, parent, nombre_tabla):
        super().__init__(parent)
        self.title(f"Agregar Columna a '{nombre_tabla}'")
        self.geometry("340x260")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.resultado = None

        lbl_titulo = ctk.CTkLabel(self, text=f"Nueva Columna para: {nombre_tabla}", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_titulo.pack(pady=(15, 10))

        self.ent_nombre = ctk.CTkEntry(self, placeholder_text="Nombre de columna (ej. nombre)", width=260)
        self.ent_nombre.pack(pady=5)

        self.combo_tipo = ctk.CTkComboBox(
            self, 
            values=["VARCHAR(100)", "INT", "TEXT", "DECIMAL(10,2)", "DATETIME", "BOOLEAN"],
            width=260
        )
        self.combo_tipo.set("VARCHAR(100)")
        self.combo_tipo.pack(pady=5)

        self.chk_pk_var = ctk.BooleanVar(value=False)
        self.chk_pk = ctk.CTkCheckBox(
            self, 
            text="¿Es Primary Key? (PK)", 
            variable=self.chk_pk_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#007AFF"
        )
        self.chk_pk.pack(pady=10)

        btn_guardar = ctk.CTkButton(self, text="Agregar Columna", command=self.confirmar, fg_color="#34C759", hover_color="#28A745")
        btn_guardar.pack(pady=10)

    def confirmar(self):
        nombre = self.ent_nombre.get().strip().replace(" ", "_")
        tipo = self.combo_tipo.get().strip()
        es_pk = self.chk_pk_var.get()
        
        if nombre and tipo:
            self.resultado = (nombre, tipo, es_pk)
            self.destroy()


class AppMySQL(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestor Local de MySQL / MariaDB - Conector Directo")
        self.geometry("1180x720")
        self.configure(fg_color="#FFFFFF")

        self.db_config = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        self.conn = None
        self.db_name = ""

        # Encabezado superior izquierdo (Descargar BD)
        self.header_left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_left_frame.place(relx=0.02, rely=0.02, anchor="nw")

        self.btn_export_db = ctk.CTkButton(
            self.header_left_frame, text="⬇️ Descargar BD (.sql)", width=150, height=28,
            fg_color="#34C759", text_color="#FFFFFF", hover_color="#28A745",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.exportar_base_de_datos_sql
        )
        self.btn_export_db.pack_forget()

        # Encabezado superior derecho (Cambiar BD)
        self.header_right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_right_frame.place(relx=0.98, rely=0.02, anchor="ne")

        self.btn_cambiar_bd = ctk.CTkButton(
            self.header_right_frame, text="🔄 Cambiar BD", width=100, height=28,
            fg_color="#E5E5EA", text_color="#007AFF", hover_color="#D1D1D6",
            command=self.mostrar_pantalla_inicio
        )
        self.btn_cambiar_bd.pack_forget()

        self.lbl_db_name = ctk.CTkLabel(
            self.header_right_frame, text="", font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#333333"
        )
        self.lbl_db_name.pack(side="right", padx=(10, 0))

        self.frame_login = None
        self.frame_inicio = None
        self.scroll_tablas = None
        self.frame_consola = None

        self.mostrar_pantalla_login()

    # ------------------ PANTALLA LOGIN DE CONEXIÓN ------------------

    def mostrar_pantalla_login(self):
        if self.frame_inicio:
            self.frame_inicio.destroy()
        if self.scroll_tablas:
            self.scroll_tablas.pack_forget()
        if self.frame_consola:
            self.frame_consola.pack_forget()

        self.frame_login = ctk.CTkFrame(self, fg_color="#F5F5F7", corner_radius=15, width=380)
        self.frame_login.place(relx=0.5, rely=0.5, anchor="center")

        lbl_titulo = ctk.CTkLabel(self.frame_login, text="Conectar a Servidor MySQL", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_titulo.pack(padx=30, pady=(20, 15))

        self.ent_host = ctk.CTkEntry(self.frame_login, placeholder_text="Host (ej. 127.0.0.1)", width=300)
        self.ent_host.insert(0, "127.0.0.1")
        self.ent_host.pack(pady=5)

        self.ent_puerto = ctk.CTkEntry(self.frame_login, placeholder_text="Puerto (ej. 3306)", width=300)
        self.ent_puerto.insert(0, "3306")
        self.ent_puerto.pack(pady=5)

        self.ent_user = ctk.CTkEntry(self.frame_login, placeholder_text="Usuario MySQL", width=300)
        self.ent_user.insert(0, "root")
        self.ent_user.pack(pady=5)

        self.ent_pass = ctk.CTkEntry(self.frame_login, placeholder_text="Contraseña", show="*", width=300)
        self.ent_pass.pack(pady=5)

        btn_conectar = ctk.CTkButton(self.frame_login, text="Conectar", width=300, height=35, command=self.probar_y_conectar_servidor)
        btn_conectar.pack(pady=(15, 20))

    def probar_y_conectar_servidor(self):
        host = self.ent_host.get().strip()
        puerto = self.ent_puerto.get().strip()
        user = self.ent_user.get().strip()
        password = self.ent_pass.get()

        if not host or not user:
            messagebox.showwarning("Atención", "Host y Usuario son requeridos.")
            return

        try:
            puerto_num = int(puerto) if puerto.isdigit() else 3306
            conn = pymysql.connect(host=host, port=puerto_num, user=user, password=password)
            conn.close()

            self.db_config = {
                'host': host,
                'port': puerto_num,
                'user': user,
                'password': password
            }
            self.frame_login.destroy()
            self.mostrar_pantalla_inicio()

        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor:\n{e}")

    # ------------------ PANTALLA INICIAL ------------------

    def mostrar_pantalla_inicio(self):
        if self.scroll_tablas:
            self.scroll_tablas.pack_forget()
        if self.frame_consola:
            self.frame_consola.pack_forget()

        self.btn_cambiar_bd.pack_forget()
        self.btn_export_db.pack_forget()
        self.lbl_db_name.configure(text="")

        if self.frame_inicio:
            self.frame_inicio.destroy()

        self.frame_inicio = ctk.CTkFrame(self, fg_color="#F5F5F7", corner_radius=15, width=450)
        self.frame_inicio.place(relx=0.5, rely=0.5, anchor="center")

        lbl_titulo = ctk.CTkLabel(self.frame_inicio, text=f"Servidor ({self.db_config['user']}@{self.db_config['host']})", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_titulo.pack(padx=30, pady=(20, 10))

        lbl_nueva = ctk.CTkLabel(self.frame_inicio, text="Crear una nueva Base de Datos:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_nueva.pack(anchor="w", padx=30, pady=(10, 5))

        frame_input = ctk.CTkFrame(self.frame_inicio, fg_color="transparent")
        frame_input.pack(fill="x", padx=30, pady=(0, 15))

        self.ent_db_name = ctk.CTkEntry(frame_input, placeholder_text="Nombre nueva BD...", height=35)
        self.ent_db_name.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_crear = ctk.CTkButton(frame_input, text="Crear", width=80, height=35, command=self.crear_y_conectar_bd)
        btn_crear.pack(side="right")

        lbl_existentes = ctk.CTkLabel(self.frame_inicio, text="O selecciona una existente del servidor:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_existentes.pack(anchor="w", padx=30, pady=(10, 5))

        scroll_bds = ctk.CTkScrollableFrame(self.frame_inicio, height=180, fg_color="#FFFFFF", corner_radius=8)
        scroll_bds.pack(fill="x", padx=30, pady=(0, 10))

        for bd in self.obtener_bases_de_datos():
            row_bd = ctk.CTkFrame(scroll_bds, fg_color="transparent")
            row_bd.pack(fill="x", pady=2)

            btn_bd = ctk.CTkButton(
                row_bd, text=f"🗄️ {bd}", anchor="w", fg_color="transparent",
                text_color="#1D1D1F", hover_color="#E5E5EA",
                command=lambda name=bd: self.seleccionar_bd_existente(name)
            )
            btn_bd.pack(side="left", fill="x", expand=True)

            btn_del_db = ctk.CTkButton(
                row_bd, text="🗑️", width=30, height=28, fg_color="transparent",
                text_color="#FF3B30", hover_color="#FFE5E5",
                command=lambda name=bd: self.eliminar_base_de_datos(name)
            )
            btn_del_db.pack(side="right", padx=(5, 0))

        btn_desconectar = ctk.CTkButton(
            self.frame_inicio, text="🔒 Cerrar Sesión / Cambiar Servidor", 
            fg_color="transparent", text_color="#007AFF", hover_color="#E5E5EA",
            command=self.mostrar_pantalla_login
        )
        btn_desconectar.pack(pady=(0, 15))

    def eliminar_base_de_datos(self, nombre_bd):
        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS `{nombre_bd}`")
            conn.close()
            self.mostrar_pantalla_inicio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la base de datos:\n{e}")

    def obtener_bases_de_datos(self):
        bds_sistema = ['information_schema', 'mysql', 'performance_schema', 'sys']
        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                todas = [row[0] for row in cursor.fetchall()]
            conn.close()
            return [bd for bd in todas if bd.lower() not in bds_sistema]
        except Exception as e:
            print(f"Error al listar BDs: {e}")
            return []

    def seleccionar_bd_existente(self, nombre_bd):
        self.db_name = nombre_bd
        if self.conectar_a_bd():
            self.iniciar_vista_tablero()

    def crear_y_conectar_bd(self):
        nombre = self.ent_db_name.get().strip().replace(" ", "_")
        if not nombre:
            return
        self.db_name = nombre
        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.db_name}`")
            conn.close()
            if self.conectar_a_bd():
                self.iniciar_vista_tablero()
        except Exception as e:
            messagebox.showerror("Error de Permisos / SQL", f"No se pudo crear la base de datos:\n{e}")

    def conectar_a_bd(self):
        try:
            self.conn = pymysql.connect(
                **self.db_config, database=self.db_name, autocommit=True
            )
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión a la base de datos:\n{e}")
            return False

    def iniciar_vista_tablero(self):
        self.frame_inicio.place_forget()
        self.lbl_db_name.configure(text=f"🗄️ {self.db_name}")
        self.btn_cambiar_bd.pack(side="left")
        self.btn_export_db.pack(side="left")

        if not self.scroll_tablas:
            self.scroll_tablas = ctk.CTkScrollableFrame(
                self, orientation="horizontal", fg_color="transparent", height=420
            )
            self.scroll_tablas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.scroll_tablas.pack(fill="x", expand=True, padx=20, pady=(50, 5))

        if not self.frame_consola:
            self.frame_consola = ctk.CTkFrame(self, fg_color="#F5F5F7", corner_radius=12)
            self.frame_consola.pack(fill="x", padx=20, pady=(5, 15))

            lbl_consola = ctk.CTkLabel(
                self.frame_consola, text="⚡ Conector Directo (Ejecutar Orden SQL):",
                font=ctk.CTkFont(size=12, weight="bold"), text_color="#1D1D1F"
            )
            lbl_consola.pack(anchor="w", padx=15, pady=(8, 2))

            box_input = ctk.CTkFrame(self.frame_consola, fg_color="transparent")
            box_input.pack(fill="x", padx=15, pady=(0, 8))

            self.ent_orden_sql = ctk.CTkEntry(
                box_input, placeholder_text="Escribe tu orden SQL...", height=35
            )
            self.ent_orden_sql.pack(side="left", fill="x", expand=True, padx=(0, 10))

            btn_ejecutar = ctk.CTkButton(
                box_input, text="Ejecutar Orden Directa", height=35, fg_color="#34C759", hover_color="#28A745",
                command=self.ejecutar_orden_directa
            )
            btn_ejecutar.pack(side="right")

            self.lbl_consola_status = ctk.CTkLabel(self.frame_consola, text="", font=ctk.CTkFont(size=11), text_color="gray50")
            self.lbl_consola_status.pack(anchor="w", padx=15, pady=(0, 5))

        else:
            self.frame_consola.pack(fill="x", padx=20, pady=(5, 15))

        self.cargar_tablero()

    # ------------------ EXPORTAR BASE DE DATOS COMPLETA A .SQL ------------------

    def exportar_base_de_datos_sql(self):
        if not self.conn or not self.db_name:
            return

        archivo_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")],
            initialfile=f"backup_{self.db_name}.sql",
            title=f"Guardar Base de Datos '{self.db_name}' como SQL"
        )

        if not archivo_path:
            return

        try:
            sql_script = f"-- Dump completo de la Base de Datos: `{self.db_name}`\n"
            sql_script += f"CREATE DATABASE IF NOT EXISTS `{self.db_name}`;\n"
            sql_script += f"USE `{self.db_name}`;\n\n"

            with self.conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tablas = [row[0] for row in cursor.fetchall()]

                for tabla in tablas:
                    sql_script += f"DROP TABLE IF EXISTS `{tabla}`;\n"
                    cursor.execute(f"SHOW CREATE TABLE `{tabla}`")
                    create_stmt = cursor.fetchone()[1]
                    sql_script += f"{create_stmt};\n\n"

                    cursor.execute(f"SELECT * FROM `{tabla}`")
                    registros = cursor.fetchall()

                    if registros:
                        for reg in registros:
                            valores = []
                            for v in reg:
                                if v is None:
                                    valores.append("NULL")
                                elif isinstance(v, (int, float)):
                                    valores.append(str(v))
                                else:
                                    val_str = str(v).replace("'", "''")
                                    valores.append(f"'{val_str}'")
                            vals_formatted = ", ".join(valores)
                            sql_script += f"INSERT INTO `{tabla}` VALUES ({vals_formatted});\n"
                        sql_script += "\n"

            with open(archivo_path, "w", encoding="utf-8") as f:
                f.write(sql_script)

            self.lbl_consola_status.configure(text=f"💾 Backup completo de BD '{self.db_name}' guardado con éxito.", text_color="#007AFF")

        except Exception as e:
            self.lbl_consola_status.configure(text=f"❌ Error al exportar la BD: {e}", text_color="#FF3B30")

    # ------------------ LÓGICA DEL CONECTOR DIRECTO Y TABLAS ------------------

    def ejecutar_orden_directa(self):
        orden_sql = self.ent_orden_sql.get().strip()
        if not orden_sql or not self.conn:
            return

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(orden_sql)
            
            self.lbl_consola_status.configure(text=f"✅ Orden ejecutada con éxito: '{orden_sql[:40]}...'", text_color="#28A745")
            self.ent_orden_sql.delete(0, 'end')
            self.cargar_tablero()

        except Exception as e:
            self.lbl_consola_status.configure(text=f"❌ Error en MySQL: {e}", text_color="#FF3B30")

    def _on_mousewheel(self, event):
        if self.scroll_tablas:
            self.scroll_tablas._parent_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def cargar_tablero(self):
        for widget in self.scroll_tablas.winfo_children():
            widget.destroy()

        if not self.conn:
            return

        with self.conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()

        for i, (nombre_tabla,) in enumerate(tablas):
            self.crear_tarjeta_tabla(nombre_tabla, i)

        posicion_boton = len(tablas)
        btn_mas = ctk.CTkButton(
            self.scroll_tablas, text="+", width=80, height=260,
            font=ctk.CTkFont(size=36, weight="bold"),
            fg_color="#E5E5EA", text_color="#007AFF", hover_color="#D1D1D6",
            corner_radius=12, command=self.crear_nueva_tabla
        )
        btn_mas.grid(row=0, column=posicion_boton, padx=15, pady=20)

    def crear_tarjeta_tabla(self, nombre_tabla, col_index):
        card = ctk.CTkFrame(
            self.scroll_tablas, width=280, height=350,
            fg_color="#F2F2F7", corner_radius=12, border_width=1, border_color="#E5E5EA"
        )
        card.grid(row=0, column=col_index, padx=15, pady=20)
        card.grid_propagate(False)

        head_frame = ctk.CTkFrame(card, fg_color="transparent")
        head_frame.pack(fill="x", padx=10, pady=(10, 5))

        lbl_titulo = ctk.CTkLabel(head_frame, text=nombre_tabla, font=ctk.CTkFont(size=15, weight="bold"), text_color="#1D1D1F")
        lbl_titulo.pack(side="left")

        btn_add_col = ctk.CTkButton(
            head_frame, text="+", width=24, height=24, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#007AFF", text_color="#FFFFFF", hover_color="#0056B3",
            command=lambda t=nombre_tabla: self.agregar_columna_tabla(t)
        )
        btn_add_col.pack(side="left", padx=(8, 0))

        btn_borrar = ctk.CTkButton(
            head_frame, text="🗑️", width=25, height=25, fg_color="transparent",
            text_color="#FF3B30", hover_color="#FFE5E5",
            command=lambda t=nombre_tabla: self.eliminar_tabla(t)
        )
        btn_borrar.pack(side="right")

        sub_frame = ctk.CTkScrollableFrame(card, fg_color="#FFFFFF", corner_radius=8)
        sub_frame.pack(fill="both", expand=True, padx=10, pady=5)

        with self.conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE `{nombre_tabla}`")
            columnas_info = cursor.fetchall()

        columnas_visibles = [col for col in columnas_info if col[0] != "id_temp"]

        if not columnas_visibles:
            lbl_vacia = ctk.CTkLabel(sub_frame, text="(Tabla vacía)", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray60")
            lbl_vacia.pack(pady=10)

        for col in columnas_visibles:
            c_name = col[0]
            c_type = col[1]
            c_key = col[3]

            row_frame = ctk.CTkFrame(sub_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)

            if c_key == "PRI":
                lbl_badge = ctk.CTkLabel(
                    info_frame, text="PK", width=26, height=18,
                    fg_color="#FFCC00", text_color="#1D1D1F",
                    corner_radius=4, font=ctk.CTkFont(size=9, weight="bold")
                )
                lbl_badge.pack(side="left", padx=(0, 5))

            lbl_col = ctk.CTkLabel(info_frame, text=f"{c_name}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#1D1D1F")
            lbl_col.pack(side="left")

            lbl_type = ctk.CTkLabel(info_frame, text=f" ({c_type})", font=ctk.CTkFont(size=10), text_color="gray50")
            lbl_type.pack(side="left")

            btn_del_col = ctk.CTkButton(
                row_frame, text="✕", width=22, height=22,
                fg_color="transparent", text_color="#FF3B30", hover_color="#FFE5E5",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda t=nombre_tabla, c=c_name: self.eliminar_columna(t, c)
            )
            btn_del_col.pack(side="right", padx=(2, 0))

    def agregar_columna_tabla(self, nombre_tabla):
        dialogo = DialogoNuevaColumna(self, nombre_tabla)
        self.wait_window(dialogo)

        if dialogo.resultado:
            col_nombre, col_tipo, es_pk = dialogo.resultado
            
            try:
                with self.conn.cursor() as cursor:
                    pk_clause = " PRIMARY KEY" if es_pk else ""
                    cursor.execute(f"ALTER TABLE `{nombre_tabla}` ADD COLUMN `{col_nombre}` {col_tipo}{pk_clause};")

                    cursor.execute(f"DESCRIBE `{nombre_tabla}`")
                    cols = [c[0] for c in cursor.fetchall()]
                    if "id_temp" in cols and len(cols) > 1:
                        cursor.execute(f"ALTER TABLE `{nombre_tabla}` DROP COLUMN `id_temp`;")

                self.lbl_consola_status.configure(text=f"✅ Columna '{col_nombre}' agregada con éxito.", text_color="#28A745")
                self.cargar_tablero()

            except Exception as e:
                self.lbl_consola_status.configure(text=f"❌ Error al agregar columna: {e}", text_color="#FF3B30")

    def eliminar_columna(self, nombre_tabla, nombre_columna):
        sql_query = f"ALTER TABLE `{nombre_tabla}` DROP COLUMN `{nombre_columna}`;"
        self.ent_orden_sql.delete(0, 'end')
        self.ent_orden_sql.insert(0, sql_query)
        self.ejecutar_orden_directa()

    def crear_nueva_tabla(self):
        dialogo = CTkInputDialog(text="Nombre de la nueva tabla:", title="Nueva Tabla")
        nombre_tabla = dialogo.get_input()
        if nombre_tabla:
            nombre_tabla = nombre_tabla.strip().replace(" ", "_")
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(f"CREATE TABLE `{nombre_tabla}` (id_temp INT);")
                self.lbl_consola_status.configure(text=f"✅ Tabla '{nombre_tabla}' creada correctamente.", text_color="#28A745")
                self.cargar_tablero()
            except Exception as e:
                self.lbl_consola_status.configure(text=f"❌ Error al crear la tabla: {e}", text_color="#FF3B30")

    def eliminar_tabla(self, nombre_tabla):
        self.ent_orden_sql.delete(0, 'end')
        self.ent_orden_sql.insert(0, f"DROP TABLE `{nombre_tabla}`;")
        self.ejecutar_orden_directa()

if __name__ == "__main__":
    app = AppMySQL()
    app.mainloop()