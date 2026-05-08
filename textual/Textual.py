# =========================
# IMPORTACIÓN DE LIBRERÍAS
# =========================
# Librerías de Textual para crear la interfaz de la aplicación
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Input, Button, Static, Select
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual import on
from textual.events import Key
from textual.binding import Binding

# Librerías para generar PDF con formato
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas

# Librerías básicas de Python
import re  # Para validaciones con expresiones regulares
import json  # Para guardar y cargar datos en formato JSON
import os  # Para manejar archivos

# =========================
# ARCHIVO DONDE SE GUARDAN LOS CLIENTES
# =========================
FICHERO = "clientes.txt"


# =========================
# FUNCIÓN PARA GUARDAR LOS CLIENTES EN EL ARCHIVO
# =========================
def guardar_txt():
    # Abrimos el archivo en modo escritura
    with open(FICHERO, "w", encoding="utf-8") as f:
        # Guardamos la lista de clientes en formato JSON
        json.dump(clientes, f, ensure_ascii=False, indent=4)


# =========================
# FUNCIÓN PARA CARGAR LOS CLIENTES DESDE EL ARCHIVO
# =========================
def cargar_txt():
    global clientes, contador_id  # Usamos variables globales

    # Comprobamos si el archivo existe
    if os.path.exists(FICHERO):

        # Abrimos el archivo en modo lectura
        with open(FICHERO, "r", encoding="utf-8") as f:

            # Leemos todo el contenido
            contenido = f.read().strip()

            # Si está vacío, no hacemos nada
            if not contenido:
                return

            # Convertimos el JSON en lista de Python
            clientes = json.loads(contenido)

        # =========================
        # RECALCULAR EL ID AUTOMÁTICO
        # =========================
        # Si hay clientes, cogemos el ID más alto y sumamos 1
        if clientes:
            contador_id = max(c[0] for c in clientes) + 1
        else:
            contador_id = 1


# =========================
# LISTA PRINCIPAL DE CLIENTES
# =========================
clientes = []

# ID que se va incrementando automáticamente
contador_id = 1


# =========================
# VALIDACIONES DE CAMPOS
# =========================

# Comprueba si el nombre está vacío
def campo_vacio_nombre(valor):
    return valor.strip() == ""


# Comprueba si los apellidos están vacíos
def campo_vacio_apellidos(valor):
    return valor.strip() == ""


# Valida formato de email
def validar_email(email):
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, email)


# Valida que el teléfono tenga 9 dígitos numéricos
def validar_telefono(telefono):
    return telefono.isdigit() and len(telefono) == 9


# Valida formato de fecha dd-mm-yyyy
def validar_cumpleanios(cumpleanios):
    patron = r"^\d{2}-\d{2}-\d{4}"
    return re.match(patron, cumpleanios)


# =========================
# GENERACIÓN DE PDF
# =========================
def exportar_pdf(lista_clientes):
    # Creamos el documento PDF
    doc = SimpleDocTemplate(
        "clientes.pdf",
        pagesize=letter,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    # Estilos del PDF
    styles = getSampleStyleSheet()
    story = []

    # Título del PDF
    titulo = Paragraph("<b>Listado de Clientes</b>", styles["Title"])
    story.append(titulo)
    story.append(Spacer(1, 0.5 * cm))

    # Cabecera de la tabla
    datos = [["ID", "Nombre", "Apellidos", "Teléfono", "Email", "Cumpleaños", "Tipo"]]

    # Añadimos cada cliente a la tabla
    for c in lista_clientes:
        datos.append([
            str(c[0]), c[1], c[2], c[3], c[4], c[5], c[6]
        ])

    # Creamos la tabla con tamaños de columnas
    tabla = Table(datos, colWidths=[1.2 * cm, 2 * cm, 3 * cm, 2.4 * cm, 4.8 * cm, 2.7 * cm, 1.8 * cm])

    # Estilo visual de la tabla
    tabla.setStyle(TableStyle([
        # Cabecera
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E4057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),

        # Filas alternas de color
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F0F4F8")
        ]),

        # Estilo del texto
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),

        # Alineaciones
        ("ALIGN", (0, 0), (0, -1), "CENTER"),  # ID
        ("ALIGN", (3, 1), (3, -1), "CENTER"),  # Teléfono
        ("ALIGN", (5, 1), (5, -1), "CENTER"),  # Cumpleaños

        # Espaciado
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),

        # Bordes
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#2E4057")),
    ]))

    # Añadimos la tabla al PDF
    story.append(tabla)

    # Generamos el archivo PDF
    doc.build(story)


# =========================
# APLICACIÓN PRINCIPAL
# =========================
class AgendaApp(App):

    # Archivo CSS de la interfaz
    CSS_PATH = "style.css"

    def compose(self) -> ComposeResult:
        # Encabezado de la app
        yield Header()

        # Selector de campo de búsqueda
        self.campo_filtro = Select(
            [
                ("Todos los campos", "todos"),
                ("Nombre", "nombre"),
                ("Apellidos", "apellidos"),
                ("Teléfono", "telefono"),
                ("Email", "email"),
                ("Cumpleaños", "cumpleaños"),
                ("Tipo", "tipo")
            ],
            value="todos",
            id="campo_filtro",
        )
        yield self.campo_filtro

        # Caja de búsqueda
        self.busqueda = Input(placeholder="Buscar cliente...")
        yield self.busqueda

        # Tabla donde se muestran los clientes
        self.tabla = DataTable()
        yield self.tabla

        # Botones de acción
        yield Horizontal(
            Button("Añadir", id="add"),
            Button("Modificar", id="modificar"),
            Button("Eliminar", id="delete"),
            Button("Exportar PDF", id="pdf"),
        )

        # Pie de la app
        yield Footer()

    # Cuando la app inicia
    def on_mount(self):
        cargar_txt()
        self.clientes_visibles = clientes
        self.tabla.add_columns(
            "ID", "Nombre", "Apellidos",
            "Teléfono", "Email", "Cumpleaños", "Tipo"
        )
        self.actualizar_tabla()

    # Actualiza la tabla con los clientes visibles
    def actualizar_tabla(self):
        self.tabla.clear()
        for c in self.clientes_visibles:
            self.tabla.add_row(
                str(c[0]), c[1], c[2],
                c[3], c[4], c[5], c[6]
            )


    # =========================
    # EVENTO: cambio en el Select (filtro de campos)
    # =========================
    def on_select_changed(self, event: Select.Changed):
        # Cuando cambia el campo del filtro (nombre, email, etc.)
        # se vuelve a ejecutar el filtrado con el texto actual de búsqueda
        self.filtrar_clientes(self.busqueda.value)


    # =========================
    # EVENTO: pulsación de botones
    # =========================
    def on_button_pressed(self, event):
        # BOTÓN AÑADIR
        if event.button.id == "add":
            # Abre la pantalla/formulario para añadir un cliente nuevo
            self.push_screen(Agregar())

        # BOTÓN MODIFICAR
        elif event.button.id == "modificar":
            # Solo si hay una fila seleccionada en la tabla
            if self.tabla.cursor_row is not None:
                # Se obtiene el cliente seleccionado según la fila
                cliente = clientes[self.tabla.cursor_row]
                # Se abre el formulario con los datos del cliente cargados
                self.push_screen(Agregar(cliente))

        # BOTÓN ELIMINAR
        elif event.button.id == "delete":
            # Solo si hay una fila seleccionada
            if self.tabla.cursor_row is not None:
                # Se obtiene el cliente seleccionado
                cliente = clientes[self.tabla.cursor_row]
                # Se abre la pantalla de confirmación de borrado
                self.push_screen(Confirmar(cliente))

        # BOTÓN EXPORTAR PDF
        elif event.button.id == "pdf":
            # Genera el PDF con los clientes filtrados actualmente
            exportar_pdf(self.clientes_visibles)
            # Muestra una notificación al usuario
            self.notify("Se ha guardado correctamente")


    # =========================
    # EVENTO: escritura en el input de búsqueda
    # =========================
    def on_input_changed(self, event: Input.Changed):
        # Solo actúa si el input cambiado es el de búsqueda
        if event.input is self.busqueda:
            # Filtra clientes cada vez que el usuario escribe algo
            self.filtrar_clientes(event.value)


    # =========================
    # FUNCIÓN: filtrado de clientes
    # =========================
    def filtrar_clientes(self, texto):
        # Se obtiene el campo seleccionado en el Select (nombre, email, etc.)
        campo = self.campo_filtro.value

        # Si el usuario no ha escrito nada, se muestran todos los clientes
        if texto.strip() == "":
            self.clientes_visibles = clientes

        else:
            # Convertimos el texto a minúsculas para comparar sin importar mayúsculas
            t = texto.lower()

            # =========================
            # FILTRO GENERAL (todos los campos)
            # =========================
            if campo == "todos":
                self.clientes_visibles = [
                    c for c in clientes
                    if t in str(c[1]).lower()  # nombre
                       or t in str(c[2]).lower()  # apellidos
                       or t in str(c[3]).lower()  # teléfono
                       or t in str(c[4]).lower()  # email
                       or t in str(c[5]).lower()  # cumpleaños
                       or t in str(c[6]).lower()  # tipo
                ]

            # =========================
            # FILTRO POR CAMPO ESPECÍFICO
            # =========================
            else:
                # Se asigna el índice según el campo seleccionado
                if campo == "id":
                    indice = 0
                elif campo == "nombre":
                    indice = 1
                elif campo == "apellidos":
                    indice = 2
                elif campo == "telefono":
                    indice = 3
                elif campo == "email":
                    indice = 4
                elif campo == "cumpleaños":
                    indice = 5
                elif campo == "tipo":
                    indice = 6

                # Se filtra comparando solo el campo seleccionado
                self.clientes_visibles = [
                    c for c in clientes
                    if t in str(c[indice]).lower()
                ]

        # Actualiza la tabla con los resultados del filtrado
        self.actualizar_tabla()

        # Atajos de teclado
    BINDINGS = [
        Binding("ctrl+Q", "salir", "Salir"),
        Binding("ctrl+a", "add", "Añadir"),
        Binding("ctrl+x", "modificar", "Modificar"),
        Binding("ctrl+d", "eliminar", "Eliminar"),
        Binding("ctrl+e", "exportar_pdf", "Exportar PDF"),
        Binding("ctrl+c", "cancelar", "Cancelar"),
        Binding("delete", "eliminar", "Eliminar")
    ]

    # ATAJO AÑADIR
    def action_add(self):
        # Abre la pantalla formulario para añadir un cliente nuevo
        self.push_screen(Agregar())

    # ATAJO MODIFICAR
    def action_modificar(self):
        # Se obtiene el cliente seleccionado según la fila
        cliente = clientes[self.tabla.cursor_row]
        # Se abre el formulario con los datos del cliente cargados
        self.push_screen(Agregar(cliente))

    # ATAJO ELIMINAR
    def action_eliminar(self):
        if self.tabla.cursor_row is not None:
            cliente = clientes[self.tabla.cursor_row]
            self.push_screen(Confirmar(cliente))

    # ATAJO EXPORTAR PDF
    def action_exportar_pdf(self):
        exportar_pdf(self.clientes_visibles)
        self.notify("PDF exportado correctamente")

    # # ATAJO GUARDAR
    # def action_guardar(self):
    #     guardado = Guardar(
    #         app=self.app,
    #         formulario=self,
    #         cliente=self.cliente,
    #         contador_id=contador_id
    #     )
    #     guardado.ejecutar()

    # ATAJO CANCELAR
    def action_cancelar(self):
        self.app.pop_screen()

# =========================
# FORMULARIO DE CLIENTES
# =========================
class Agregar(Screen):

        # Constructor: recibe un cliente si estamos editando
        def __init__(self, cliente=None):
            super().__init__()
            self.cliente = cliente

        # Construcción de la interfaz del formulario
        def compose(self) -> ComposeResult:

            # Campo nombre (relleno si estamos editando)
            self.nombre = Input(
                value=self.cliente[1] if self.cliente else "",
                placeholder="Nombre"
            )

            # Campo apellidos
            self.apellido = Input(
                value=self.cliente[2] if self.cliente else "",
                placeholder="Apellido"
            )

            # Campo teléfono
            self.telefono = Input(
                value=self.cliente[3] if self.cliente else "",
                placeholder="Teléfono"
            )

            # Campo email
            self.email = Input(
                value=self.cliente[4] if self.cliente else "",
                placeholder="Email"
            )

            # Campo cumpleaños
            self.cumpleanios = Input(
                value=self.cliente[5] if self.cliente else "",
                placeholder="Cumpleaños"
            )

            # Select tipo de cliente
            self.tipo = Select(
                options=[
                    ("particular", "particular"),
                    ("empresa", "empresa")
                ],
                value="particular"
            )

            # Se muestran todos los campos en pantalla
            yield Vertical(
                Static("Editar Cliente" if self.cliente else "Nuevo Cliente"),
                self.nombre,
                self.apellido,
                self.telefono,
                self.email,
                self.cumpleanios,
                self.tipo,
                id="formulario"
            )

            # Botones del formulario
            yield Horizontal(
                Button("Guardar", id="save"),
                Button("Cancelar", id="cancel")
            )

        # Cuando se abre la pantalla
        def on_mount(self):
            # Si estamos editando, se carga el tipo del cliente
            if self.cliente:
                self.tipo.value = self.cliente[6]

        # =========================
        # BOTONES DEL FORMULARIO
        # =========================
        def on_button_pressed(self, event):
            global contador_id

            # GUARDAR CLIENTE
            if event.button.id == "save":
                guardado = Guardar(
                    app=self.app,
                    formulario=self,
                    cliente=self.cliente,
                    contador_id=contador_id
                )
                guardado.ejecutar()

            elif event.button.id == "cancel":
                self.app.pop_screen()


# =========================
# GUARDAR
# =========================
class Guardar:
    def __init__(self, app, formulario, cliente, contador_id):
        self.app = app
        self.formulario = formulario
        self.cliente = cliente
        self.contador_id = contador_id

    def ejecutar(self):
        global clientes

        # =========================
        # VALIDACIONES
        # =========================
        if campo_vacio_nombre(self.formulario.nombre.value):
            self.app.notify("El nombre está vacío")
            return

        if campo_vacio_apellidos(self.formulario.apellido.value):
            self.app.notify("Apellidos está vacío")
            return

        if not validar_email(self.formulario.email.value):
            self.app.notify("Email no válido")
            return

        if not validar_telefono(self.formulario.telefono.value):
            self.app.notify("Teléfono no válido (9 dígitos)")
            return

        if not validar_cumpleanios(self.formulario.cumpleanios.value):
            self.app.notify("El formato de la fecha de cumpleaños no es correcto (dd-mm-yyyy)")
            return

        # =========================
        # EDITAR
        # =========================
        if self.cliente:
            self.cliente[1] = self.formulario.nombre.value
            self.cliente[2] = self.formulario.apellido.value
            self.cliente[3] = self.formulario.telefono.value
            self.cliente[4] = self.formulario.email.value
            self.cliente[5] = self.formulario.cumpleanios.value
            self.cliente[6] = self.formulario.tipo.value

        # =========================
        # NUEVO
        # =========================
        else:
            clientes.append([
                self.contador_id,
                self.formulario.nombre.value,
                self.formulario.apellido.value,
                self.formulario.telefono.value,
                self.formulario.email.value,
                self.formulario.cumpleanios.value,
                str(self.formulario.tipo.value)
            ])
           # self.app.incrementar_id()

        guardar_txt()
        self.app.pop_screen()
        self.app.actualizar_tabla()

# =========================
# PANTALLA DE CONFIRMACIÓN
# =========================
class Confirmar(Screen):

        def __init__(self, cliente):
            super().__init__()
            self.cliente = cliente

        def compose(self) -> ComposeResult:
            nombre_completo = f"{self.cliente[1]} {self.cliente[2]}"

            # Mensaje de confirmación
            yield Vertical(
                Static(f"¿Eliminar a {nombre_completo}?"),
                Horizontal(
                    Button("Sí, eliminar", id="confirmar"),
                    Button("Cancelar", id="cancelar")
                )
            )

        def on_button_pressed(self, event):

            # CONFIRMAR BORRADO
            if event.button.id == "confirmar":
                clientes.remove(self.cliente)
                guardar_txt()
                self.app.pop_screen()
                self.app.actualizar_tabla()

            # CANCELAR BORRADO
            elif event.button.id == "cancelar":
                self.app.pop_screen()


# =========================
# EJECUCIÓN DEL PROGRAMA
# =========================
if __name__ == "__main__":
    app = AgendaApp()
    app.run()
