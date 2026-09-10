import wx

from win32com.client import Dispatch

import threading
import os
import sys
import subprocess
import tempfile
import yt_dlp
import shutil
import winsound
import traceback
import webbrowser
from MotorV8 import MotorV8
from MotorConfiguracion import MotorConfiguracion

def obtener_ruta(nombre):
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)

        for ruta in (
            os.path.join(base, "_internal", nombre),
            os.path.join(base, nombre),
            os.path.join(sys._MEIPASS, nombre),
        ):
            if os.path.exists(ruta):
                return ruta

        return os.path.join(
            base,
            "_internal",
            nombre
        )

    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        nombre
    )


def registrar_error(
    mensaje,
    incluirTraceback=True
):

    try:

        ruta = obtener_ruta(
            "error.log"
        )

        carpeta = os.path.dirname(
            ruta
        )

        if not os.path.exists(
            carpeta
        ):

            os.makedirs(
                carpeta,
                exist_ok=True
            )

        from datetime import datetime

        fecha = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with open(
            ruta,
            "a",
            encoding="utf-8"
        ) as f:

            f.write("\n")
            f.write("=" * 70)
            f.write("\n")
            f.write(
                "Fecha y hora: "
                + fecha
                + "\n"
            )
            f.write(
                "Mensaje: "
                + str(mensaje)
                + "\n"
            )

            if incluirTraceback:

                detalle = (
                    traceback.format_exc()
                )

                if (
                    detalle
                    and detalle.strip()
                    != "NoneType: None"
                ):

                    f.write(
                        "\n"
                    )

                    f.write(
                        "Detalles técnicos:\n"
                    )

                    f.write(
                        detalle
                    )

            f.write("\n")

    except Exception:

        pass


class VentanaPlaylist(wx.Dialog):

    def __init__(
        self,
        parent,
        titulo,
        items
    ):

        super().__init__(
            parent,
            title=titulo,
            size=(700, 600)
        )

        self.items_data = items

        sizer = wx.BoxSizer(
            wx.VERTICAL
        )

        instruccion = wx.StaticText(
            self,
            label=(
                "Marque con ESPACIO y pulse TAB "
                "hasta 'Descargar Seleccionados'."
            )
        )

        instruccion.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD
            )
        )

        self.check_list = wx.CheckListBox(
            self,
            choices=[
                i.get(
                    "title",
                    "Video"
                )
                for i in items
            ]
        )

        self.check_list.Bind(
            wx.EVT_CHECKLISTBOX,
            self.al_seleccionar
        )

        self.check_list.Bind(
            wx.EVT_LISTBOX,
            self.al_mover_lista
        )

        self.check_list.SetFont(
            wx.Font(
                16,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD
            )
        )

        self.btn_descargar = wx.Button(
            self,
            label="Descargar seleccionados (0)"
        )

        self.btn_descargar.SetFont(
            wx.Font(
                16,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD
            )
        )

        self.btn_descargar.Enable(
            False
        )

        self.btn_cancelar = wx.Button(
            self,
            label="Cancelar"
        )

        self.btn_cancelar.SetFont(
            wx.Font(
                16,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD
            )
        )

        sizer.Add(
            instruccion,
            0,
            wx.ALL,
            10
        )

        sizer.Add(
            self.check_list,
            1,
            wx.EXPAND | wx.ALL,
            10
        )

        sizer.Add(
            self.btn_descargar,
            0,
            wx.ALIGN_CENTER | wx.ALL,
            15
        )

        sizer.Add(
            self.btn_cancelar,
            0,
            wx.ALIGN_CENTER | wx.ALL,
            15
        )

        self.SetSizer(
            sizer
        )

        self.btn_descargar.Bind(
            wx.EVT_BUTTON,
            self.al_descargar
        )

        self.btn_cancelar.Bind(
            wx.EVT_BUTTON,
            self.al_cancelar
        )

        self.seleccionados = []

    def hablar(
        self,
        texto
    ):

        self.GetParent().hablar(
            texto
        )

    def al_seleccionar(
        self,
        event
    ):

        indice = event.GetSelection()

        if indice != wx.NOT_FOUND:

            titulo = self.check_list.GetString(
                indice
            )

            marcado = self.check_list.IsChecked(
                indice
            )

            if marcado:

                self.hablar(
                    "Seleccionado"
                )

                ruta_click = obtener_ruta(
                    "Click.wav"
                )

                if os.path.exists(
                    ruta_click
                ):

                    winsound.PlaySound(
                        ruta_click,
                        winsound.SND_FILENAME
                        | winsound.SND_ASYNC
                    )

            else:

                self.hablar(
                    "des marcado."
                )

            ruta_click = obtener_ruta(
                "Click.wav"
            )

            if os.path.exists(
                ruta_click
            ):

                winsound.PlaySound(
                    ruta_click,
                    winsound.SND_FILENAME
                    | winsound.SND_ASYNC
                )

            self.actualizar_estado_descarga()

        event.Skip()

    def al_mover_lista(
        self,
        event
    ):

        indice = self.check_list.GetSelection()

        if indice != wx.NOT_FOUND:

            if self.check_list.IsChecked(
                indice
            ):

                self.hablar(
                    "Seleccionado"
                )

            else:

                self.hablar(
                    "No seleccionado"
                )

        event.Skip()

    def actualizar_estado_descarga(
        self
    ):

        indices = self.check_list.GetCheckedItems()

        cantidad = len(
            indices
        )

        self.btn_descargar.SetLabel(
            f"Descargar seleccionados ({cantidad})"
        )

        self.btn_descargar.Enable(
            cantidad > 0
        )

        if cantidad > 0:

            if cantidad == 1:

                self.hablar(
                    "1 archivo seleccionado."
                )

            else:

                self.hablar(
                    f"{cantidad} archivos seleccionados."
                )

    def al_cancelar(
        self,
        e=None
    ):

        self.EndModal(
            wx.ID_CANCEL
        )

    def al_descargar(
        self,
        e
    ):

        indices = self.check_list.GetCheckedItems()

        cantidad = len(
            indices
        )

        self.seleccionados = [
            self.items_data[i]
            for i in indices
        ]

        if cantidad > 0:

            self.hablar(
                f"{cantidad} archivos seleccionados."
            )

            self.EndModal(
                wx.ID_OK
            )

def es_url_multimedia(url):

    url = url.lower()

    extensiones = (

        ".mp3",
        ".aac",
        ".ogg",
        ".opus",
        ".wav",
        ".flac",
        ".m4a",
        ".mp4",
        ".mkv",
        ".webm",
        ".m3u8",
        ".pls"

    )

    if url.endswith(extensiones):

        return True

    palabras = (

        "stream",
        "radio",
        "live",
        "audio",
        "video",
        "podcast",
        "icecast",
        "shoutcast",
        "listen",
        "broadcast",
        "fm",
        "am"

    )

    for palabra in palabras:

        if palabra in url:

            return True

    return False


def buscar_reproductor():

    candidatos = [

        r"C:\Program Files\DAUM\PotPlayer\PotPlayerMini64.exe",

        r"C:\Program Files\DAUM\PotPlayer\PotPlayerMini.exe",

        r"C:\Program Files\VideoLAN\VLC\vlc.exe",

        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",

        r"C:\Program Files\MPC-HC\mpc-hc64.exe",

        r"C:\Program Files\MPC-HC\mpc-hc.exe"

    ]

    for exe in candidatos:

        if os.path.exists(exe):

            return exe

    return None


class JustiApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="JustiDownloadPRO_2.0.0 ", size=(1000, 950))
        self.buscando = False
        self.enlaces = []
        self.detalles_videos = []
        self.destino = os.path.join(os.path.expanduser("~"), "Documents", "JustiDownloads")
        if not os.path.exists(self.destino): os.makedirs(self.destino)
        self.volumenVoz = 60

        self.voz = Dispatch("SAPI.SpVoice")
        self.voz.Volume = 60
        self.voz.Rate = 0
        self.motor = MotorV8()
        # =========================================================
        # Configuración persistente junto al ejecutable
        # =========================================================

        if getattr(sys, "frozen", False):

            carpeta_config = os.path.dirname(
                sys.executable
            )

        else:

            carpeta_config = os.path.dirname(
                os.path.abspath(__file__)
            )

        archivo_config_nuevo = os.path.join(
            carpeta_config,
            "JustiConfig.json"
        )

        archivo_config_antiguo = os.path.join(
            self.destino,
            "JustiConfig.json"
        )

        if (
            not os.path.exists(archivo_config_nuevo)
            and os.path.exists(archivo_config_antiguo)
        ):

            try:

                shutil.copy2(
                    archivo_config_antiguo,
                    archivo_config_nuevo
                )

            except Exception:

                log.exception(
                    "No se pudo migrar JustiConfig.json"
                )

        self.config = MotorConfiguracion(
            carpeta_config
        )

        self.volumenVoz = self.config.obtener(
            "volumen",
            60
        )

        vozGuardada = self.config.obtener(
            "vozSapi5"
        )

        if vozGuardada:

            try:

                voces = self.voz.GetVoices()

                for i in range(
                    voces.Count
                ):

                    voz = voces.Item(
                        i
                    )

                    if (
                        voz.GetDescription()
                        == vozGuardada
                    ):

                        self.voz.Voice = (
                            voz
                        )

                        break

            except Exception:

                log.exception(
                    "Error restaurando voz SAPI 5"
                )

        self.formatoActual = self.config.obtener(
            "formato",
            "mp3"
        )
        self.calidadActual = self.config.obtener(
            "calidad",
            "192"
        )
        carpeta = self.config.obtener(

            "carpetaDescargas",

            ""

        )

        if carpeta and os.path.isdir(carpeta):

            self.destino = carpeta
        self.fuente_gigante = wx.Font(22, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.fuente_boton = wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        panel_p = wx.Panel(self)
        panel_p.SetBackgroundColour(wx.Colour(117, 170, 219)) 
        sizer_base = wx.BoxSizer(wx.VERTICAL)

        img_path = obtener_ruta("LOGO JUSTICIA CIEGA.jpg")
        if os.path.exists(img_path):
            try:
                img = wx.Image(img_path, wx.BITMAP_TYPE_ANY).Scale(500, 500, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.StaticBitmap(panel_p, wx.ID_ANY, wx.Bitmap(img))
                sizer_base.Add(bmp, 0, wx.ALIGN_CENTER | wx.ALL, 15)
            except: pass

        self.nb = wx.Notebook(panel_p)
        self.p1 = wx.Panel(self.nb); self.p1.SetBackgroundColour(wx.WHITE)
        sz1 = wx.BoxSizer(wx.VERTICAL)
        
        lbl_guia = wx.StaticText(self.p1, label="Pega el Texto o enlace Aquí:")
        lbl_guia.SetFont(self.fuente_gigante)
        self.txt = wx.TextCtrl(self.p1, style=wx.TE_PROCESS_ENTER)

        self.cantidadResultados = 15

        self.txt.Bind(
            wx.EVT_CONTEXT_MENU,
            self.mostrar_menu_resultados
        )

        self.txt.SetFont(self.fuente_gigante)
        
        fila_config = wx.BoxSizer(wx.HORIZONTAL)

        fila_config.Add(wx.StaticText(self.p1, label="Formato:"), 0, wx.CENTER | wx.LEFT, 5)
        self.cmb_fmt = wx.Choice(self.p1, choices=["mp3", "mp4", "m4a", "wav"])
        self.cmb_fmt.SetFont(self.fuente_boton)
        indice = self.cmb_fmt.FindString(
            self.formatoActual
        )

        if indice == wx.NOT_FOUND:

            indice = 0

        self.cmb_fmt.SetSelection(
            indice
        )


        fila_config.Add(wx.StaticText(self.p1, label="Calidad:"), 0, wx.CENTER | wx.LEFT, 10)
        self.cmb_qual = wx.Choice(self.p1, choices=["128", "192", "256", "320"])
        self.cmb_qual.SetFont(self.fuente_boton)

        indice = self.cmb_qual.FindString(
            self.calidadActual
        )

        if indice == wx.NOT_FOUND:

            indice = 1

        self.cmb_qual.SetSelection(
            indice
        )

        fila_config.Add(
            wx.StaticText(
                self.p1,
                label="Volumen:"
            ),
            0,
            wx.CENTER | wx.LEFT,
            10
        )

        self.sliderVol = wx.Slider(
            self.p1,
            value=60,
            minValue=0,
            maxValue=100,
            style=wx.SL_HORIZONTAL
        )

        fila_config.Add(
            self.sliderVol,
            1,
            wx.ALL | wx.EXPAND,
            5
        )

        self.btn_dir = wx.Button(self.p1, label="Carpeta (Alt+C)")
        self.btn_dir.SetFont(self.fuente_boton)
        self.btn_dir.SetFont(self.fuente_boton)

        self.btn_voz = wx.Button(
            self.p1,
            label="Cambiar voz SAPI 5"
        )

        self.btn_voz.SetFont(
            self.fuente_boton
        )

        self.btn_voz.Bind(
            wx.EVT_BUTTON,
            self.cambiar_voz_sapi
        )

        fila_config.Add(
            self.cmb_fmt,
            1,
            wx.ALL,
            5
        )

        fila_config.Add(
            self.cmb_qual,
            1,
            wx.ALL,
            5
        )

        fila_config.Add(
            self.btn_dir,
            1,
            wx.ALL,
            5
        )

        self.chk_autoAbrir = wx.CheckBox(
            self.p1,
            label="Abrir automáticamente"
        )

        self.chk_autoAbrir.SetFont(
            self.fuente_boton
        )

        self.chk_autoAbrir.SetValue(

            self.config.obtener(

                "abrirAutomaticamente",

                False

            )

        )

        fila_config.Add(

            self.chk_autoAbrir,

            1,

            wx.ALL | wx.CENTER,

            5

        )
        
        self.btn_b = wx.Button(self.p1, label="BUSCAR (Alt+B)")
        self.btn_b.SetBackgroundColour(wx.Colour(255, 230, 0)); self.btn_b.SetFont(self.fuente_boton)
        self.lst = wx.ListBox(self.p1, style=wx.LB_SINGLE); self.lst.SetFont(self.fuente_gigante)
        self.gauge = wx.Gauge(self.p1, range=100)
        
        sz_btns = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_d = wx.Button(self.p1, label="DESCARGAR (Alt+D)")
        self.btn_d.SetBackgroundColour(wx.Colour(200, 0, 0)); self.btn_d.SetForegroundColour(wx.WHITE); self.btn_d.SetFont(self.fuente_boton)
        self.btn_l = wx.Button(self.p1, label="LIMPIAR (Alt+L)")
        self.btn_l.SetBackgroundColour(wx.Colour(0, 150, 0)); self.btn_l.SetForegroundColour(wx.WHITE); self.btn_l.SetFont(self.fuente_boton)
        
        sz_btns.Add(self.btn_d, 2, wx.EXPAND | wx.ALL, 5); sz_btns.Add(self.btn_l, 1, wx.EXPAND | wx.ALL, 5)
        
        sz1.Add(lbl_guia, 0, wx.ALL, 5); sz1.Add(self.txt, 0, wx.EXPAND | wx.ALL, 5)
        sz1.Add(fila_config, 0, wx.EXPAND | wx.ALL, 5); sz1.Add(self.btn_b, 0, wx.EXPAND | wx.ALL, 5)
        sz1.Add(self.lst, 1, wx.EXPAND | wx.ALL, 10); sz1.Add(self.gauge, 0, wx.EXPAND | wx.ALL, 10); sz1.Add(sz_btns, 0, wx.EXPAND | wx.ALL, 5)

        self.lst.MoveAfterInTabOrder(self.txt)

        self.cmb_fmt.MoveAfterInTabOrder(self.lst)

        self.cmb_qual.MoveAfterInTabOrder(self.cmb_fmt)

        self.btn_d.MoveAfterInTabOrder(self.cmb_qual)

        self.btn_l.MoveAfterInTabOrder(self.btn_d)

        self.btn_dir.MoveAfterInTabOrder(self.btn_l)

        self.sliderVol.MoveAfterInTabOrder(self.btn_dir)

        self.btn_b.MoveAfterInTabOrder(self.sliderVol)
        self.p1.SetSizer(sz1)

        self.lst.MoveAfterInTabOrder(self.txt)

        self.cmb_fmt.MoveAfterInTabOrder(self.lst)

        self.cmb_qual.MoveAfterInTabOrder(self.cmb_fmt)

        self.btn_d.MoveAfterInTabOrder(self.cmb_qual)

        self.btn_l.MoveAfterInTabOrder(self.btn_d)

        self.btn_dir.MoveAfterInTabOrder(self.btn_l)

        self.sliderVol.MoveAfterInTabOrder(self.btn_dir)

        self.btn_b.MoveAfterInTabOrder(self.sliderVol)

        self.p2 = wx.Panel(self.nb); self.p2.SetBackgroundColour(wx.WHITE)
        sz2 = wx.BoxSizer(wx.VERTICAL)
        self.btn_m = wx.Button(self.p2, label="ABRIR MANUAL Y CONTACTO")
        self.btn_m.SetFont(self.fuente_gigante)
        sz2.Add(self.btn_m, 1, wx.EXPAND | wx.ALL, 50); self.p2.SetSizer(sz2)

        self.nb.AddPage(self.p1, "BUSCADOR"); self.nb.AddPage(self.p2, "MANUAL")
        sizer_base.Add(self.nb, 1, wx.EXPAND | wx.ALL, 5); panel_p.SetSizer(sizer_base)

        self.setup_shortcuts()
        self.btn_b.Bind(wx.EVT_BUTTON, self.ejecutar_busqueda)
        self.btn_d.Bind(wx.EVT_BUTTON, self.descargar_seleccion)
        self.btn_l.Bind(wx.EVT_BUTTON, self.limpiar_campos)
        self.btn_m.Bind(wx.EVT_BUTTON, self.abrir_manual)
        self.btn_dir.Bind(wx.EVT_BUTTON, self.seleccionar_carpeta)
        self.chk_autoAbrir.Bind(

            wx.EVT_CHECKBOX,

            self.alCambiarAutoAbrir

        )
        self.lst.Bind(wx.EVT_CONTEXT_MENU, self.mostrar_menu)

        self.txt.Bind(wx.EVT_TEXT_ENTER, self.ejecutar_busqueda)

        self.sliderVol.Bind(
            wx.EVT_SLIDER,
            self.cambiarVolumen
        )
        self.cmb_fmt.Bind(
            wx.EVT_CHOICE,
            self.alCambiarFormato
        )

        self.cmb_qual.Bind(
            wx.EVT_CHOICE,
            self.alCambiarCalidad
        )

        self.sliderVol.SetValue(

            self.config.obtener(

                "volumen",

                60

            )

        )

        self.voz = Dispatch("SAPI.SpVoice")

        self.voz.Volume = self.config.obtener(

            "volumen",

            60

        )

        self.voz.Rate = 0

        vozGuardada = self.config.obtener(
            "vozSapi5",
            ""
        )

        if vozGuardada:

            try:

                voces = self.voz.GetVoices()

                for i in range(
                    voces.Count
                ):

                    voz = voces.Item(
                        i
                    )

                    if (
                        voz.GetDescription()
                        == vozGuardada
                    ):

                        self.voz.Voice = voz

                        break

            except Exception:

                log.exception(
                    "Error restaurando voz SAPI 5"
                )

        self.Show()
        wx.CallLater(
    600,
    self.hablar,
    "Bienvenido a JustiDownload dos punto cero."
)

        wx.CallAfter(
            self.txt.SetFocus
        )

        wx.CallAfter(
            self.txt.SelectAll
        )

        wx.CallAfter(
            self.txt.SetFocus
        )

        wx.CallAfter(
            self.txt.SelectAll
        )

        wx.CallAfter(
            self.txt.SetInsertionPointEnd
        )

    def setup_shortcuts(self):
        IDs = [wx.NewIdRef() for _ in range(9)]
        self.SetAcceleratorTable(wx.AcceleratorTable([
            (wx.ACCEL_ALT, ord('B'), IDs[0]), (wx.ACCEL_ALT, ord('1'), IDs[1]),
            (wx.ACCEL_ALT, ord('2'), IDs[2]), (wx.ACCEL_ALT, ord('D'), IDs[3]),
            (wx.ACCEL_ALT, ord('L'), IDs[4]), (wx.ACCEL_ALT, ord('R'), IDs[5]),
            (wx.ACCEL_ALT, ord('I'), IDs[6]), (wx.ACCEL_ALT, wx.WXK_LEFT, IDs[7]),
            (wx.ACCEL_ALT, ord('C'), IDs[8])
        ]))
        self.Bind(wx.EVT_MENU, self.ejecutar_busqueda, id=IDs[0])
        self.Bind(wx.EVT_MENU, lambda e: self.nb.SetSelection(0), id=IDs[1])
        self.Bind(wx.EVT_MENU, lambda e: self.nb.SetSelection(1), id=IDs[2])
        self.Bind(wx.EVT_MENU, self.descargar_seleccion, id=IDs[3])
        self.Bind(wx.EVT_MENU, self.limpiar_campos, id=IDs[4])
        self.Bind(wx.EVT_MENU, self.reproducir, id=IDs[5])
        self.Bind(wx.EVT_MENU, self.ver_info, id=IDs[6])
        self.Bind(wx.EVT_MENU, self.retroceso_inteligente, id=IDs[7])
        self.Bind(wx.EVT_MENU, self.seleccionar_carpeta, id=IDs[8])

    def seleccionar_carpeta(
        self,
        e=None
    ):

        with wx.DirDialog(

            self,

            "Seleccioná la carpeta",

            defaultPath=self.destino,

            style=wx.DD_DEFAULT_STYLE

        ) as dlg:

            if dlg.ShowModal() == wx.ID_OK:

                self.destino = dlg.GetPath()

                self.config.establecer(

                    "carpetaDescargas",

                    self.destino

                )

                self.hablar(

                    f"Carpeta: {os.path.basename(self.destino)}"

                )

    def retroceso_inteligente(self, e):
        self.nb.SetSelection(0); self.limpiar_campos(); self.hablar("Regresando al inicio")

    def abrir_manual(self, e):
        ruta = obtener_ruta("manual.html")
        if os.path.exists(ruta): webbrowser.open(f"file:///{os.path.abspath(ruta)}"); self.hablar("Abriendo")
        else: self.hablar("Manual no encontrado.")

    def sonido_busqueda(self):
        while self.buscando: winsound.Beep(650, 60)

    def mostrar_menu_resultados(
        self,
        event
    ):

        menu = wx.Menu()

        opciones = [

            (15, "15 resultados"),
            (25, "25 resultados"),
            (50, "50 resultados"),
            (100, "100 resultados"),
            (250, "250 resultados"),
            (500, "500 resultados"),
            (1000, "1000 resultados")

        ]

        for cantidad, texto in opciones:

            item = menu.Append(
                wx.ID_ANY,
                texto,
                kind=wx.ITEM_CHECK
            )

            item.Check(
                cantidad
                == self.cantidadResultados
            )

            self.Bind(
                wx.EVT_MENU,
                lambda e, n=cantidad:
                    self.seleccionar_cantidad_resultados(
                        e,
                        n
                    ),
                item
            )

        self.PopupMenu(
            menu
        )

        menu.Destroy()


    def seleccionar_cantidad_resultados(
        self,
        event,
        cantidad
    ):

        self.cantidadResultados = cantidad

        wx.Bell()

    def ejecutar_busqueda(
        self,
        e=None
    ):

        q = self.txt.GetValue().strip()

        if q and not self.buscando:

            self.buscando = True

            self.hablar(
                "Buscando"
            )

            threading.Thread(
                target=self.sonido_busqueda,
                daemon=True
            ).start()

            threading.Thread(
                target=self.hilo_busqueda,
                args=(q,),
                daemon=True
            ).start()

    def hilo_busqueda(
        self,
        q
    ):

        es_url = q.lower().startswith(
            "http"
        )

        es_playlist = (
            es_url
            and "list=" in q.lower()
        )

        ydl_opts = {

            "quiet": True,

            "extract_flat": True

        }

        if es_playlist:

            ydl_opts["noplaylist"] = False

        query = (

            f"ytsearch{self.cantidadResultados}:{q}"

            if not es_url

            else q

        )

        try:

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                info = ydl.extract_info(
                    query,
                    download=False
                )

                if es_playlist:

                    info["_type"] = "playlist"

                    info["webpage_url"] = q

                    res = [
                        info
                    ]

                else:

                    res = (

                        info.get(
                            "entries",
                            [info]
                        )

                        if "entries"
                        in info

                        else [info]
                    )

                wx.CallAfter(
                    self.llenar_lista,
                    res
                )

        except Exception:

            registrar_error(
                "Error de red durante la búsqueda"
            )

            wx.CallAfter(
                self.hablar,
                "Error de red"
            )

        finally:

            self.buscando = False

    def llenar_lista(self, res):

        self.lst.Clear()

        self.enlaces = []

        self.detalles_videos = []

        for r in res:

            if r:

                self.lst.Append(

                    r.get(

                        "title",

                        "Video"

                    )

                )

                url = (

                    r.get(

                        "webpage_url"

                    )

                    or r.get(

                        "url"

                    )

                )

                tipo = "playlist" if r.get("_type") == "playlist" else "video"

                self.enlaces.append(

                    {

                        "url": url,

                        "tipo": tipo,

                        "playlist": r.get("playlist"),

                        "titulo": r.get("title", "")

                    }

                )

                self.detalles_videos.append(

                    r

                )

        if self.lst.GetCount() > 0:

            self.lst.SetSelection(

                0

            )

            self.lst.SetFocus()

    def mostrar_menu(
        self,
        e
    ):

        idx = self.lst.GetSelection()

        if idx == -1:

            return

        m = wx.Menu()

        m.Append(
            101,
            "Reproducir (Alt+R)"
        )

        sm_desc = wx.Menu()

        sm_desc.Append(
            102,
            "Video Actual"
        )

        sm_plist = wx.Menu()

        sm_plist.Append(
            103,
            "Playlist Completa"
        )

        sm_plist.Append(
            104,
            "&Playlist Personalizada"
        )

        sm_desc.AppendSubMenu(
            sm_plist,
            "Playlist"
        )

        m.AppendSubMenu(
            sm_desc,
            "Descargar"
        )

        m.Append(
            105,
            "Información (Alt+I)"
        )

        self.Bind(
            wx.EVT_MENU,
            self.reproducir,
            id=101
        )

        self.Bind(
            wx.EVT_MENU,
            self.descargar_seleccion,
            id=102
        )

        self.Bind(
            wx.EVT_MENU,
            self.descargar_playlist_completa,
            id=103
        )

        self.Bind(
            wx.EVT_MENU,
            self.abrir_playlist_personalizada,
            id=104
        )

        self.Bind(
            wx.EVT_MENU,
            self.ver_info,
            id=105
        )

        self.PopupMenu(
            m
        )

        m.Destroy()

    def abrir_playlist_personalizada(
        self,
        e=None
    ):

        idx = self.lst.GetSelection()

        if idx == wx.NOT_FOUND:

            self.hablar(
                "Ningún elemento seleccionado."
            )

            return

        item = self.enlaces[idx]

        if item.get("tipo") != "playlist":

            self.hablar(
                "No es una playlist."
            )

            return

        url = item.get(
            "url",
            ""
        )

        if not url:

            self.hablar(
                "No se encontró la dirección."
            )

            return

        self.hablar(
            "Procesando playlist"
        )

        threading.Thread(
            target=self.hilo_playlist_personalizada,
            args=(url,),
            daemon=True
        ).start()

    def hilo_playlist_personalizada(
        self,
        url
    ):

        ydl_opts = {

            "quiet": True,

            "extract_flat": True,

            "skip_download": True,

            "ignoreerrors": True

        }

        try:

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                info = ydl.extract_info(
                    url,
                    download=False
                )

            entradas = info.get(
                "entries",
                []
            )

            resultados = []

            for entrada in entradas:

                if not entrada:

                    continue

                entrada = dict(
                    entrada
                )

                video_url = (

                    entrada.get(
                        "webpage_url"
                    )

                    or entrada.get(
                        "original_url"
                    )

                    or entrada.get(
                        "url"
                    )

                )

                if not video_url:

                    continue

                entrada["webpage_url"] = video_url

                resultados.append(
                    entrada
                )

            if not resultados:

                wx.CallAfter(
                    self.hablar,
                    "La playlist no contiene videos disponibles."
                )

                return

            wx.CallAfter(
                self.mostrar_playlist_personalizada,
                resultados
            )

        except Exception:

            registrar_error(
                "Error procesando playlist personalizada"
            )

            log.exception(
                "Error procesando playlist personalizada"
            )

            wx.CallAfter(
                self.hablar,
                "No se pudo procesar la playlist."
            )

    def mostrar_playlist_personalizada(
        self,
        items
    ):

        dlg = VentanaPlaylist(
            self,
            "Playlist Personalizada",
            items
        )

        try:

            if dlg.ShowModal() == wx.ID_OK:

                urls = [

                    v.get(
                        "webpage_url"
                    )

                    or v.get(
                        "url"
                    )

                    for v in dlg.seleccionados

                ]

                urls = [

                    url

                    for url in urls

                    if url

                ]

                if urls:

                    self.lanzar_hilo(
                        urls,
                        abrir_al_final=True
                    )

                else:

                    self.hablar(
                        "No se seleccionaron videos."
                    )

        finally:

            dlg.Destroy()

    def lanzar_hilo(
        self,
        urls,
        abrir_al_final=False
    ):

        fmt = self.cmb_fmt.GetStringSelection()

        qual = self.cmb_qual.GetStringSelection()

        threading.Thread(
            target=self.hilo_descarga,
            args=(
                urls,
                fmt,
                qual,
                abrir_al_final
            ),
            daemon=True
        ).start()


    def hablar(
        self,
        texto
    ):
        """
        Verbaliza un mensaje utilizando
        la voz SAPI 5 del sistema.
        """

        def _say():

            try:

                self.voz.Volume = self.volumenVoz

                self.voz.Speak(
                    str(texto),
                    1
                )

            except Exception:

                pass

        threading.Thread(
            target=_say,
            daemon=True
        ).start()

    def reproducir(
        self,
        e=None
    ):

        idx = self.lst.GetSelection()

        if idx == -1:

            return

        item = self.enlaces[idx]

        ok, dato = self.motor.ejecutar_con_retorno(

            item["url"]

        )

        if not ok:

            self.hablar(
            "Error en la reproducción"
        )

    def ver_info(
        self,
        e=None
    ):

        idx = self.lst.GetSelection()

        if idx == wx.NOT_FOUND:

            self.hablar(
                "Ningún elemento seleccionado."
            )

            return

        try:

            v = self.detalles_videos[idx]

            tipo = v.get(
                "_type",
                ""
            )

            url = (
                v.get("webpage_url")
                or v.get("original_url")
                or v.get("url")
                or ""
            )

            if not url:

                self.hablar(
                    "No se encontró el enlace."
                )

                return

            if (
                tipo == "playlist"
                or v.get("playlist")
                or self.enlaces[idx].get("tipo") == "playlist"
            ):

                titulo = v.get(
                    "title",
                    "Playlist sin título"
                )

                canal = v.get(
                    "uploader",
                    "No disponible"
                )

                informacion = (
                    "Nombre de la playlist: "
                    + str(titulo)
                    + "\n"
                    + "Nombre del canal: "
                    + str(canal)
                    + "\n"
                    + "Enlace: "
                    + str(url)
                )

                self.hablar(
                    "Obteniendo información"
                )

                self.mostrar_ventana_info(
                    informacion,
                    url
                )

                return

            titulo = v.get(
                "title",
                "No disponible"
            )

            canal = v.get(
                "uploader",
                "No disponible"
            )

            self.hablar(
                "Obteniendo información"
            )

            threading.Thread(
                target=self.hilo_info_video,
                args=(
                    url,
                    titulo,
                    canal
                ),
                daemon=True
            ).start()

        except Exception:

            log.exception(
                "Error iniciando información"
            )

            self.hablar(
                "No se pudo obtener la información."
            )

    def hilo_info_video(
        self,
        url,
        titulo,
        canal
    ):

        ydl_opts = {
            "quiet": True,
            "skip_download": True
        }

        try:

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                info = ydl.extract_info(
                    url,
                    download=False
                )

            titulo = (
                info.get("title")
                or titulo
            )

            canal = (
                info.get("uploader")
                or info.get("channel")
                or canal
            )

            suscriptores = info.get(
                "channel_follower_count"
            )

            likes = info.get(
                "like_count"
            )

            comentarios = info.get(
                "comment_count"
            )

            url_final = (
                info.get("webpage_url")
                or info.get("original_url")
                or url
            )

            wx.CallAfter(
                self.mostrar_info_video,
                titulo,
                canal,
                suscriptores,
                likes,
                comentarios,
                url_final
            )

        except Exception:

            log.exception(
                "Error obteniendo metadatos del video"
            )

            wx.CallAfter(
                self.hablar,
                "No se pudo obtener la información del video."
            )

    def mostrar_info_video(
        self,
        titulo,
        canal,
        suscriptores,
        likes,
        comentarios,
        url
    ):

        if suscriptores is None:

            suscriptoresTexto = "No disponible"

        else:

            suscriptoresTexto = str(
                suscriptores
            )

        if likes is None:

            likesTexto = "No disponible"

        else:

            likesTexto = str(
                likes
            )

        if comentarios is None:

            comentariosTexto = "No disponible"

        else:

            comentariosTexto = str(
                comentarios
            )

        informacion = (
            "Nombre del video: "
            + str(titulo)
            + "\n"
            + "Nombre del canal: "
            + str(canal)
            + "\n"
            + "Cantidad de suscriptores: "
            + suscriptoresTexto
            + "\n"
            + "Cantidad de me gusta: "
            + likesTexto
            + "\n"
            + "Cantidad de comentarios: "
            + comentariosTexto
            + "\n"
            + "Enlace: "
            + str(url)
        )

        self.mostrar_ventana_info(
            informacion,
            url
        )

    def mostrar_ventana_info(
        self,
        informacion,
        url
    ):

        dlg = wx.Dialog(
            self,
            title="Información del video",
            size=(700, 400)
        )

        panel = wx.Panel(
            dlg
        )

        vbox = wx.BoxSizer(
            wx.VERTICAL
        )

        txtInfo = wx.TextCtrl(
            panel,
            value=informacion,
            style=(
                wx.TE_MULTILINE
                | wx.TE_READONLY
            )
        )

        btnCopiarEnlace = wx.Button(
            panel,
            label="Copiar enlace"
        )

        btnCopiarTodo = wx.Button(
            panel,
            label="Copiar toda la información"
        )

        btnCerrar = wx.Button(
            panel,
            wx.ID_CANCEL,
            "Cerrar"
        )

        def copiar_texto(
            texto
        ):

            try:

                if wx.TheClipboard.Open():

                    wx.TheClipboard.SetData(
                        wx.TextDataObject(
                            texto
                        )
                    )

                    wx.TheClipboard.Close()

                    wx.Bell()

                    self.hablar(
                        "Copiada."
                    )

            except Exception:

                log.exception(
                    "Error copiando información"
                )

                self.hablar(
                    "No se copio la info."
                )

        def copiar_enlace(
            event
        ):

            copiar_texto(
                url
            )

        def copiar_todo(
            event
        ):

            copiar_texto(
                informacion
            )

        btnCopiarEnlace.Bind(
            wx.EVT_BUTTON,
            copiar_enlace
        )

        btnCopiarTodo.Bind(
            wx.EVT_BUTTON,
            copiar_todo
        )

        vbox.Add(
            txtInfo,
            1,
            wx.EXPAND | wx.ALL,
            10
        )

        vbox.Add(
            btnCopiarEnlace,
            0,
            wx.EXPAND
            | wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM,
            10
        )

        vbox.Add(
            btnCopiarTodo,
            0,
            wx.EXPAND
            | wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM,
            10
        )

        vbox.Add(
            btnCerrar,
            0,
            wx.ALIGN_RIGHT | wx.ALL,
            10
        )

        panel.SetSizer(
            vbox
        )

        txtInfo.SetFocus()

        dlg.ShowModal()

        dlg.Destroy(
)

    def cambiar_voz_sapi(
        self,
        event=None
    ):

        try:

            voces = self.voz.GetVoices()

            if voces.Count == 0:

                self.hablar(
                    "No se encontraron voces."
                )

                return

            nombres = []

            for i in range(
                voces.Count
            ):

                voz = voces.Item(
                    i
                )

                nombres.append(
                    voz.GetDescription()
                )

            dlg = wx.SingleChoiceDialog(
                self,
                "Seleccione la voz SAPI 5:",
                "Cambiar voz SAPI 5",
                nombres
            )

            if dlg.ShowModal() == wx.ID_OK:

                seleccion = dlg.GetSelection()

                if seleccion != wx.NOT_FOUND:

                    vozSeleccionada = voces.Item(
                        seleccion
                    )

                    self.voz.Voice = (
                        vozSeleccionada
                    )

                    nombreVoz = (
                        vozSeleccionada.GetDescription()
                    )

                    self.config.establecer(
                        "vozSapi5",
                        nombreVoz
                    )

                    self.hablar(
    "Voz cambiada."
)

            dlg.Destroy()

        except Exception:

            log.exception(
                "Error cambiando voz SAPI 5"
            )

            self.hablar(
                "No se pudo cambiar."
            )

        def mostrar(
            nombre,
            valor
        ):

            if valor is None:

                return (
                    f"{nombre}: "
                    "No disponible"
                )

            return (
                f"{nombre}: "
                f"{valor}"
            )

        informacion = "\n".join([

            f"Nombre del video: {titulo}",

            f"Nombre del canal: {canal}",

            mostrar(
                "Cantidad de suscriptores",
                suscriptores
            ),

            mostrar(
                "Cantidad de me gusta",
                likes
            ),

            mostrar(
                "Cantidad de comentarios",
                comentarios
            ),

            f"Enlace: {url}"

        ])

        dlg = wx.Dialog(
            self,
            title="Información del video",
            size=(700, 400)
        )

        panel = wx.Panel(
            dlg
        )

        vbox = wx.BoxSizer(
            wx.VERTICAL
        )

        txtInfo = wx.TextCtrl(
            panel,
            value=informacion,
            style=(
                wx.TE_MULTILINE
                | wx.TE_READONLY
            )
        )

        btnCopiarEnlace = wx.Button(
            panel,
            label="Copiar enlace"
        )

        btnCopiarTodo = wx.Button(
            panel,
            label="Copiar toda la información"
        )

        btnCerrar = wx.Button(
            panel,
            wx.ID_CANCEL,
            "Cerrar"
        )

        def copiar_enlace(
            event
        ):

            if url:

                if wx.TheClipboard.Open():

                    wx.TheClipboard.SetData(
                        wx.TextDataObject(
                            url
                        )
                    )

                    wx.TheClipboard.Close()

                    wx.Bell()

        def copiar_todo(
            event
        ):

            if wx.TheClipboard.Open():

                wx.TheClipboard.SetData(
                    wx.TextDataObject(
                        informacion
                    )
                )

                wx.TheClipboard.Close()

                wx.Bell()

        btnCopiarEnlace.Bind(
            wx.EVT_BUTTON,
            copiar_enlace
        )

        btnCopiarTodo.Bind(
            wx.EVT_BUTTON,
            copiar_todo
        )

        vbox.Add(
            txtInfo,
            1,
            wx.EXPAND | wx.ALL,
            10
        )

        vbox.Add(
            btnCopiarEnlace,
            0,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            10
        )

        vbox.Add(
            btnCopiarTodo,
            0,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            10
        )

        vbox.Add(
            btnCerrar,
            0,
            wx.ALIGN_RIGHT | wx.ALL,
            10
        )

        panel.SetSizer(
            vbox
        )

        dlg.SetEscapeId(
            wx.ID_CANCEL
        )

        txtInfo.SetFocus()

        dlg.ShowModal()

        dlg.Destroy()

    def descargar_seleccion(
        self,
        e=None
    ):

        idx = self.lst.GetSelection()

        if idx == wx.NOT_FOUND:

            self.hablar(

                "Ningún video seleccionado"

            )

            return

        item = self.enlaces[idx]

        url = item["url"]

        if item["tipo"] == "playlist":

            self.hablar(

                "Este elemento es una playlist. Utilice el menú Playlist."

            )

            return

        if not url:

            self.hablar(

                "No se encontró la dirección"

            )

            return

        self.lanzar_hilo(
            [url]
        )

    def descargar_playlist_completa(
        self,
        e=None
    ):

        idx = self.lst.GetSelection()

        if idx == wx.NOT_FOUND:

            self.hablar(

                "Ningún elemento seleccionado"

            )

            return

        item = self.enlaces[idx]

        url = item["url"]

        self.lanzar_hilo(
            [url],
            abrir_al_final=True
        )

    def hilo_descarga(
        self,
        urls,
        fmt,
        qual,
        abrir_al_final=False
    ):

        archivoFinal = None

        archivosAntes = set(

            os.listdir(

                self.destino

            )

        )

        ydl_opts = {

            "ignoreerrors": True,

            "outtmpl": os.path.join(
                self.destino,
                "%(title)s.%(ext)s"
            ),

            "ignoreerrors": True,

            "ffmpeg_location": obtener_ruta(
                "ffmpeg.exe"
            ),

            "js_runtimes": {
                "deno": {
                    "path": obtener_ruta(
                        "deno.exe"
                    )
                }
            },

            "progress_hooks": [
                self.progreso_hook
            ],

        "postprocessor_hooks": [
            self.postprocesado_hook
        ]
    }

        if fmt == "mp4":

            ydl_opts.update({

                "format": "bv*+ba/b",

                "merge_output_format": "mp4"

            })

        else:

            ydl_opts.update({

                "format": "bestaudio/best",

                "postprocessors": [{

                    "key": "FFmpegExtractAudio",

                    "preferredcodec": fmt,

                    "preferredquality": qual

                }]

            })

        try:

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                for url in urls:

                    try:

                        info = ydl.extract_info(
                            url,
                            download=False
                        )

                        if not info:

                            continue

                        if info.get(
                            "_type"
                        ) == "playlist":

                            entradas = info.get(
                                "entries",
                                []
                            )

                            for entrada in entradas:

                                if not entrada:

                                    continue

                                video_url = (
                                    entrada.get(
                                        "webpage_url"
                                    )
                                    or entrada.get(
                                        "original_url"
                                    )
                                    or entrada.get(
                                        "url"
                                    )
                                )

                                if not video_url:

                                    continue

                                try:

                                    ydl.download(
                                        [video_url]
                                    )

                                except Exception:

                                    registrar_error(
                                        "Elemento no disponible en playlist: "
                                        + str(video_url)
                                    )

                                    continue

                        else:

                            ydl.download(
                                [url]
                            )

                    except Exception:

                        registrar_error(
                            "Elemento no disponible en playlist: "
                            + str(url)
                        )

                        continue

            archivosDespues = set(
                os.listdir(
                    self.destino
                )
            )

            nuevos = list(
                archivosDespues - archivosAntes
            )

            if not nuevos:

                wx.CallAfter(
                    self.hablar,
                    "No se pudo completar la descarga."
                )

                return

            prioridad = [
                "." + fmt,
                ".mp3",
                ".wav",
                ".m4a",
                ".mp4"
            ]

            elegido = None

            for extension in prioridad:

                for archivo in nuevos:

                    if archivo.lower().endswith(
                        extension
                    ):

                        elegido = archivo

                        break

                if elegido:

                    break

            if not elegido:

                elegido = nuevos[0]

            self.archivoFinal = os.path.join(
                self.destino,
                elegido
            )

            wx.CallAfter(
                self.hablar,
                "Descarga completada"
            )

            if (
                self.config.obtener(
                    "abrirAutomaticamente",
                    False
                )
                and (
                    abrir_al_final
                    or len(urls) == 1
                )
                and self.archivoFinal
            ):

                try:

                    os.startfile(
                        self.archivoFinal
                    )

                except Exception:

                    pass

        except Exception:

            registrar_error(
                "Error en descarga"
            )

            wx.CallAfter(
                self.hablar,
                "Error en descarga"
            )

    def postprocesado_hook(

        self,

        datos

    ):

        try:

            if datos.get(

                "status"

            ) == "finished":

                self.archivoFinal = datos.get(

                    "filename"

                )

        except Exception:

            self.archivoFinal = None


    def progreso_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','').strip()
            try: prog = int(float(p)); wx.CallAfter(self.gauge.SetValue, prog); winsound.Beep(
    350 + (prog * 2),
    20
)
            except: pass

    def limpiar_campos(self, e=None):
        self.txt.Clear(); self.lst.Clear(); self.gauge.SetValue(0); self.hablar("Limpiado"); self.txt.SetFocus()

    def cambiarVolumen(self, event):

        self.volumenVoz = self.sliderVol.GetValue()

        self.voz.Volume = self.volumenVoz

        self.config.establecer(

            "volumen",

            self.volumenVoz

        )

    def alCambiarFormato(
        self,
        event
    ):

        self.config.establecer(

            "formato",

            self.cmb_fmt.GetStringSelection()

        )
    def alCambiarCalidad(
        self,
        event
    ):

        self.config.establecer(

            "calidad",

            self.cmb_qual.GetStringSelection()

        )
    def alCambiarAutoAbrir(

        self,

        event

    ):

        self.config.establecer(

            "abrirAutomaticamente",

            self.chk_autoAbrir.GetValue()

        )
    def guardarVolumenConfiguracion(
    self,
    event
):

        self.voz.Volume = self.sliderVol.GetValue()

        self.config.establecer(

            "volumen",

            self.sliderVol.GetValue()

        )

if __name__ == "__main__":

    app = wx.App(False)

    ventana = JustiApp()

    app.MainLoop()
