import wx
import pyttsx3
import threading
import os
import sys
import yt_dlp
import winsound
import webbrowser

def obtener_ruta(nombre):
    if getattr(sys, 'frozen', False):
        base_exe = os.path.dirname(sys.executable)
        ruta_interna = os.path.join(base_exe, "_internal", nombre)
        if os.path.exists(ruta_interna): return ruta_interna
        return os.path.join(sys._MEIPASS, nombre)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, nombre)

class VentanaPlaylist(wx.Dialog):
    def __init__(self, parent, titulo, items):
        super().__init__(parent, title=titulo, size=(700, 600))
        self.items_data = items
        sizer = wx.BoxSizer(wx.VERTICAL)
        instruccion = wx.StaticText(self, label="Marque con ESPACIO los videos y pulse TAB hasta 'Descargar Seleccionados'.")
        instruccion.SetFont(wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.check_list = wx.CheckListBox(self, choices=[i.get('title', 'Video') for i in items])
        self.check_list.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.btn_descargar = wx.Button(self, label="Descargar Seleccionados")
        self.btn_descargar.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(instruccion, 0, wx.ALL, 10)
        sizer.Add(self.check_list, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.btn_descargar, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        self.SetSizer(sizer)
        self.btn_descargar.Bind(wx.EVT_BUTTON, self.al_descargar)
        self.seleccionados = []

    def al_descargar(self, e):
        indices = self.check_list.GetCheckedItems()
        self.seleccionados = [self.items_data[i] for i in indices]
        if not self.seleccionados: return
        self.EndModal(wx.ID_OK)

class JustiApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="JustiDownloadPRO_1.0 - Justicia Ciega", size=(1000, 950))
        self.buscando = False
        self.enlaces = []
        self.detalles_videos = []
        self.destino = os.path.join(os.path.expanduser("~"), "Documents", "JustiDownloads")
        if not os.path.exists(self.destino): os.makedirs(self.destino)

        self.fuente_gigante = wx.Font(22, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.fuente_boton = wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        try: self.SetIcon(wx.Icon(obtener_ruta("logo_justicia_ciega.ico")))
        except: pass

        panel_principal = wx.Panel(self)
        panel_principal.SetBackgroundColour(wx.Colour(117, 170, 219)) 
        sizer_base = wx.BoxSizer(wx.VERTICAL)

        img_path = obtener_ruta("LOGO JUSTICIA CIEGA.jpg")
        if os.path.exists(img_path):
            try:
                img = wx.Image(img_path, wx.BITMAP_TYPE_ANY).Scale(500, 500, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.StaticBitmap(panel_principal, wx.ID_ANY, wx.Bitmap(img))
                sizer_base.Add(bmp, 0, wx.ALIGN_CENTER | wx.ALL, 15)
            except: pass

        self.nb = wx.Notebook(panel_principal)
        self.p1 = wx.Panel(self.nb); self.p1.SetBackgroundColour(wx.WHITE)
        sz1 = wx.BoxSizer(wx.VERTICAL)
        
        lbl_guia = wx.StaticText(self.p1, label="Pega el Texto o enlace Aquí:")
        lbl_guia.SetFont(self.fuente_gigante)
        self.txt = wx.TextCtrl(self.p1, style=wx.TE_PROCESS_ENTER)
        self.txt.SetFont(self.fuente_gigante)
        
        fila_config = wx.BoxSizer(wx.HORIZONTAL)
        self.cmb_formato = wx.Choice(self.p1, choices=["mp3", "mp4", "m4a", "wav"])
        self.cmb_formato.SetFont(self.fuente_boton); self.cmb_formato.SetSelection(0)
        
        lbl_bitrate = wx.StaticText(self.p1, label=" Calidad Bitrate:")
        lbl_bitrate.SetFont(self.fuente_boton)
        self.cmb_vibrato = wx.Choice(self.p1, choices=["128", "192", "256", "320"])
        self.cmb_vibrato.SetFont(self.fuente_boton); self.cmb_vibrato.SetSelection(0)

        fila_config.Add(self.cmb_formato, 1, wx.EXPAND | wx.ALL, 5)
        fila_config.Add(lbl_bitrate, 0, wx.ALIGN_CENTER)
        fila_config.Add(self.cmb_vibrato, 1, wx.EXPAND | wx.ALL, 5)
        
        self.btn_buscar = wx.Button(self.p1, label="BUSCAR (Alt+B)")
        self.btn_buscar.SetBackgroundColour(wx.Colour(255, 230, 0)); self.btn_buscar.SetFont(self.fuente_boton)
        self.lst = wx.ListBox(self.p1, style=wx.LB_SINGLE); self.lst.SetFont(self.fuente_gigante)
        self.gauge = wx.Gauge(self.p1, range=100)
        
        sz_btns = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_descargar = wx.Button(self.p1, label="DESCARGAR (Alt+D)")
        self.btn_descargar.SetBackgroundColour(wx.Colour(200, 0, 0)); self.btn_descargar.SetForegroundColour(wx.WHITE); self.btn_descargar.SetFont(self.fuente_boton)
        self.btn_limpiar = wx.Button(self.p1, label="LIMPIAR (Alt+L)")
        self.btn_limpiar.SetBackgroundColour(wx.Colour(0, 150, 0)); self.btn_limpiar.SetForegroundColour(wx.WHITE); self.btn_limpiar.SetFont(self.fuente_boton)
        
        sz_btns.Add(self.btn_descargar, 2, wx.EXPAND | wx.ALL, 5); sz_btns.Add(self.btn_limpiar, 1, wx.EXPAND | wx.ALL, 5)
        
        sz1.Add(lbl_guia, 0, wx.ALL, 5); sz1.Add(self.txt, 0, wx.EXPAND | wx.ALL, 5)
        sz1.Add(fila_config, 0, wx.EXPAND | wx.ALL, 5); sz1.Add(self.btn_buscar, 0, wx.EXPAND | wx.ALL, 5)
        sz1.Add(self.lst, 1, wx.EXPAND | wx.ALL, 10); sz1.Add(self.gauge, 0, wx.EXPAND | wx.ALL, 10); sz1.Add(sz_btns, 0, wx.EXPAND | wx.ALL, 5)
        self.p1.SetSizer(sz1)

        self.p2 = wx.Panel(self.nb); self.p2.SetBackgroundColour(wx.WHITE)
        sz2 = wx.BoxSizer(wx.VERTICAL)
        self.btn_abrir_manual = wx.Button(self.p2, label="ABRIR MANUAL Y CONTACTO")
        self.btn_abrir_manual.SetFont(self.fuente_gigante)
        sz2.Add(self.btn_abrir_manual, 1, wx.EXPAND | wx.ALL, 50); self.p2.SetSizer(sz2)

        self.nb.AddPage(self.p1, "BUSCADOR"); self.nb.AddPage(self.p2, "MANUAL")
        sizer_base.Add(self.nb, 1, wx.EXPAND | wx.ALL, 5); panel_principal.SetSizer(sizer_base)

        self.setup_shortcuts()
        self.btn_buscar.Bind(wx.EVT_BUTTON, self.ejecutar_busqueda)
        self.btn_descargar.Bind(wx.EVT_BUTTON, self.descargar_seleccion)
        self.btn_limpiar.Bind(wx.EVT_BUTTON, self.limpiar_campos)
        self.btn_abrir_manual.Bind(wx.EVT_BUTTON, self.abrir_manual)
        self.lst.Bind(wx.EVT_CONTEXT_MENU, self.mostrar_menu)
        self.txt.Bind(wx.EVT_TEXT_ENTER, self.ejecutar_busqueda)
        self.Show(); self.hablar("¡Bienvenidos! ¡soy JustiDownload!")

    def setup_shortcuts(self):
        IDs = [wx.NewIdRef() for _ in range(8)]
        self.SetAcceleratorTable(wx.AcceleratorTable([
            (wx.ACCEL_ALT, ord('B'), IDs[0]), (wx.ACCEL_ALT, ord('1'), IDs[1]),
            (wx.ACCEL_ALT, ord('2'), IDs[2]), (wx.ACCEL_ALT, ord('D'), IDs[3]),
            (wx.ACCEL_ALT, ord('L'), IDs[4]), (wx.ACCEL_ALT, ord('R'), IDs[5]),
            (wx.ACCEL_ALT, ord('I'), IDs[6]), (wx.ACCEL_ALT, wx.WXK_LEFT, IDs[7])
        ]))
        self.Bind(wx.EVT_MENU, self.ejecutar_busqueda, id=IDs[0])
        self.Bind(wx.EVT_MENU, lambda e: self.nb.SetSelection(0), id=IDs[1])
        self.Bind(wx.EVT_MENU, lambda e: self.nb.SetSelection(1), id=IDs[2])
        self.Bind(wx.EVT_MENU, self.descargar_seleccion, id=IDs[3])
        self.Bind(wx.EVT_MENU, self.limpiar_campos, id=IDs[4])
        self.Bind(wx.EVT_MENU, self.reproducir, id=IDs[5])
        self.Bind(wx.EVT_MENU, self.ver_info, id=IDs[6])
        self.Bind(wx.EVT_MENU, self.retroceso_inteligente, id=IDs[7])

    def retroceso_inteligente(self, e):
        self.nb.SetSelection(0); self.limpiar_campos(); self.hablar("Regresando al inicio")

    def abrir_manual(self, e):
        ruta = obtener_ruta("manual.html")
        if os.path.exists(ruta): webbrowser.open(f"file:///{os.path.abspath(ruta)}"); self.hablar("Abriendo manual")
        else: self.hablar("Manual no encontrado.")

    def sonido_busqueda(self):
        while self.buscando: winsound.Beep(900, 150); winsound.Beep(1100, 150)

    def ejecutar_busqueda(self, e=None):
        q = self.txt.GetValue().strip()
        if q and not self.buscando:
            self.buscando = True; self.hablar("Buscando")
            threading.Thread(target=self.sonido_busqueda, daemon=True).start()
            threading.Thread(target=self.hilo_busqueda, args=(q,), daemon=True).start()

    def hilo_busqueda(self, q):
        ydl_opts = {'quiet': True, 'extract_flat': 'in_playlist', 'nocheckcertificate': True}
        query = f"ytsearch15:{q}" if not q.startswith('http') else q
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                res = info.get('entries', [info]) if 'entries' in info else [info]
                wx.CallAfter(self.llenar_lista, res)
        except: wx.CallAfter(self.hablar, "Error de red")
        finally: self.buscando = False

    def llenar_lista(self, res):
        self.lst.Clear(); self.enlaces = []; self.detalles_videos = []
        for r in res:
            if r:
                self.lst.Append(r.get('title', 'Video'))
                self.enlaces.append(r.get('webpage_url') or r.get('url')); self.detalles_videos.append(r)
        if self.lst.GetCount() > 0: self.lst.SetSelection(0); self.lst.SetFocus(); self.hablar(f"Listo. {self.lst.GetCount()} resultados")

    def mostrar_menu(self, e):
        idx = self.lst.GetSelection()
        if idx == -1: return
        m = wx.Menu()
        repro = m.Append(wx.ID_ANY, "Reproducir (Alt+R)")
        m.AppendSeparator(); sm_desc = wx.Menu(); vid_act = sm_desc.Append(wx.ID_ANY, "Video Actual")
        sm_plist = wx.Menu(); pl_comp = sm_plist.Append(wx.ID_ANY, "Playlist Completa"); pl_pers = sm_plist.Append(wx.ID_ANY, "Playlist Personalizada")
        sm_desc.AppendSubMenu(sm_plist, "Playlist"); m.AppendSubMenu(sm_desc, "Descargar"); info = m.Append(wx.ID_ANY, "Información (Alt+I)")
        self.Bind(wx.EVT_MENU, self.reproducir, repro); self.Bind(wx.EVT_MENU, self.descargar_seleccion, vid_act)
        self.Bind(wx.EVT_MENU, lambda e: self.lanzar_hilo(self.enlaces), pl_comp); self.Bind(wx.EVT_MENU, self.abrir_playlist_personalizada, pl_pers); self.Bind(wx.EVT_MENU, self.ver_info, info)
        self.PopupMenu(m); m.Destroy()

    def abrir_playlist_personalizada(self, e):
        dlg = VentanaPlaylist(self, "Playlist Personalizada", self.detalles_videos)
        if dlg.ShowModal() == wx.ID_OK:
            urls = [v.get('webpage_url') or v.get('url') for v in dlg.seleccionados]
            self.lanzar_hilo(urls)
        dlg.Destroy()

    def lanzar_hilo(self, urls):
        fmt = self.cmb_formato.GetStringSelection(); qual = self.cmb_vibrato.GetStringSelection()
        threading.Thread(target=self.hilo_descarga, args=(urls, fmt, qual), daemon=True).start()

    def hablar(self, t):
        def _say():
            try: e = pyttsx3.init(); e.say(t); e.runAndWait()
            except: pass
        threading.Thread(target=_say, daemon=True).start()

    def reproducir(self, e=None):
        idx = self.lst.GetSelection()
        if idx != -1: webbrowser.open(self.enlaces[idx])

    def ver_info(self, e=None):
        idx = self.lst.GetSelection()
        if idx != -1:
            v = self.detalles_videos[idx]; self.hablar(f"Título: {v.get('title')}. Canal: {v.get('uploader')}")

    def descargar_seleccion(self, e=None):
        idx = self.lst.GetSelection()
        if idx != -1: self.lanzar_hilo([self.enlaces[idx]])

    def hilo_descarga(self, urls, fmt, qual):
        ydl_opts = {'outtmpl': os.path.join(self.destino, '%(title)s.%(ext)s'), 'ffmpeg_location': obtener_ruta("ffmpeg.exe"), 'progress_hooks': [self.progreso_hook]}
        if fmt != "mp4": ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': fmt,'preferredquality': qual}]})
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download(urls)
            wx.CallAfter(self.hablar, "Descarga completada")
        except: wx.CallAfter(self.hablar, "Error en descarga")

    def progreso_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','').strip()
            try: prog = int(float(p)); wx.CallAfter(self.gauge.SetValue, prog); winsound.Beep(600 + (prog * 4), 40)
            except: pass

    def limpiar_campos(self, e=None):
        self.txt.Clear(); self.lst.Clear(); self.gauge.SetValue(0); self.hablar("Limpiado"); self.txt.SetFocus()

if __name__ == "__main__":
    app = wx.App(); JustiApp(); app.MainLoop()