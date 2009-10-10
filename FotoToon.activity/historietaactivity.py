# -*- coding: UTF8 -*-

import os
import math
import gtk
import gobject
import cairo
import pango

import globos
import persistencia

from sugar.activity import activity

from toolbar import TextToolbar
from toolbar import GlobesToolbar

class HistorietaActivity(activity.Activity):
    def __init__(self, handle):
        print "INICIALIZANDO HISTORIETA"
        activity.Activity.__init__(self, handle)
        self.set_title('Historieta')
        
        self.connect("key_press_event", self.keypress)
    
        toolbox = activity.ActivityToolbox(self)
        
        self.pagina = Pagina()

        self.globesToolbar = GlobesToolbar(self.pagina)
        toolbox.add_toolbar('Globos', self.globesToolbar)

        # fonts (pendiente)
        self.textToolbar = TextToolbar(self.pagina)
        toolbox.add_toolbar('Texto', self.textToolbar)
    
        self.set_toolbox(toolbox)
        toolbox.show_all()
        toolbox.set_current_toolbar(1)        

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scrolled.add_with_viewport(self.pagina)
        scrolled.show_all()
        self.set_canvas(scrolled)
        self.show()

    def keypress(self, widget, event):
        if (self.pagina.get_cuadro_activo() != None):
            self.pagina.get_cuadro_activo().keypress(event.string,event.keyval)

    
    def setWaitCursor( self ):
        self.window.set_cursor( gtk.gdk.Cursor(gtk.gdk.WATCH) )

    def setDefaultCursor( self ):
        self.window.set_cursor( None )
        
    def write_file(self, file_path):
        print "file path",file_path
        writer = persistencia.Writer()
        writer.write(file_path,self.pagina)


DEF_SPACING = 6
DEF_WIDTH = 4

SCREEN_HEIGHT = gtk.gdk.screen_height()
SCREEN_WIDTH = gtk.gdk.screen_width()

class Pagina(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self,False,0)        
        self.set_homogeneous(False)

        self.cuadros = []
        self._cuadro_activo = None

        # Agrego cuadro titulo
        self.cuadro_titulo = Cuadro(None)
        self.cuadro_titulo.show()
        self.cuadro_titulo.set_size_request(SCREEN_WIDTH,100)
        self.pack_start(self.cuadro_titulo,False)        
        self.set_cuadro_activo(self.cuadro_titulo)
        self.cuadros.append(self.cuadro_titulo)
        self.cuadro_titulo.pagina = self

        # Agrego tabla para las fotos
        self.table = gtk.Table(10, 2, True)
        self.table.set_homogeneous(True)
        self.table.set_row_spacings(DEF_SPACING)
        self.table.set_col_spacings(DEF_SPACING)
        self.pack_start(self.table)        

    def add_photo(self):
        appdir = activity.get_bundle_path()
        '''
        posi = len(self.cuadros)-1
        cuadro = Cuadro(os.path.join(appdir,'fotos/foto'+str(posi)+'.png'))
        cuadro.show()
        reng = int(posi / 2)
        column = posi - (reng * 2)
        self.attach(cuadro,column,column+1,reng+1,reng+2)
        '''
        posi = len(self.cuadros) - 1

        num_foto = posi -  (posi / 4) * 4
        cuadro = Cuadro(os.path.join(appdir,'fotos/foto'+str(num_foto)+'.png'))
        cuadro.show()
        reng = int(posi / 2) 
        column = posi - (reng * 2)
        self.table.attach(cuadro,column,column+1,reng,reng+1)
        self.set_cuadro_activo(cuadro)
        self.cuadros.append(cuadro)
        cuadro.pagina = self

    def set_cuadro_activo(self,cuadro):
        cuadro_anterior = None 
        if (self._cuadro_activo != None):
            cuadro_anterior =  self._cuadro_activo
        self._cuadro_activo = cuadro
        cuadro.queue_draw()
        if (cuadro_anterior != None):
            cuadro_anterior.queue_draw()            

    def get_cuadro_activo(self):
        return self._cuadro_activo

    def get_globo_activo(self):
        cuadro = self.get_cuadro_activo()
        if cuadro != None:
            if (cuadro.globo_activo != None):
                return cuadro.globo_activo
        return None


class Cuadro(gtk.DrawingArea):

    def __init__(self, image_name):
        print ("Cuadro INIT")
        gtk.DrawingArea.__init__(self)
        #se agregan los eventos de pulsación y movimiento del ratón
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK \
                        |gtk.gdk.BUTTON1_MOTION_MASK)

        #self.globos es una lista que contiene los globos de ese cuadro
        self.globos = []
        
        #self.pixbuf = pixbuf
        self.glob_press = False
        self.is_dimension = False
        self.is_punto = False
        self.pagina = None
        self.image_name = ""

        if (image_name != None):
            self.image = cairo.ImageSurface.create_from_png (image_name)
            self.image_name = image_name
        else:
            self.image = None

        self.globo_activo = None

        self.set_size_request(-1,450)

        self.connect("expose_event", self.expose)
        self.connect("button_press_event", self.pressing)
        self.connect("motion_notify_event", self.moving)
        self.connect("button_release_event", self.releassing)
        self.queue_draw()

    #def get_size_request(self)
    #    return 100,100
        
    def add_globo(self,xpos,ypos,gmodo="normal",gdireccion=globos.DIR_ABAJO):
        #agrega un globo al cuadro
        globo = globos.Globo(x=xpos,y=ypos,modo=gmodo,direccion=gdireccion)
        self.globos.append(globo)
        self.globo_activo = globo
        self.queue_draw()
    
    def add_rectangulo(self,xpos,ypos):
        #agrega un cuadro de texto al cuadro
        self.globos.append(globos.Rectangulo(x=xpos,y=ypos))
        self.queue_draw()
    
    def add_nube(self,xpos,ypos):
        #agrega un globo de pensamiento al cuadro
        globo = globos.Nube(x=xpos,y=ypos)
        self.globos.append(globo)
        self.globo_activo = globo
        self.queue_draw()

    def add_imagen(self,xpos,ypos):
        #agrega una imagen al cuadro
        globo = globos.Imagen(x=xpos,y=ypos)
        self.globos.append(globo)
        self.globo_activo = globo
        self.queue_draw()
    
    def add_grito(self,xpos,ypos):
        #agrega un globo de grito al cuadro
        globo = globos.Grito(x=xpos,y=ypos)
        self.globos.append(globo)
        self.globo_activo = globo
        self.queue_draw()
     
    def expose(self,widget,event):
        self.context = widget.window.cairo_create()
        self.draw(self.context, event.area)
        return False

    def set_sink(self, sink):
        assert self.window.xid
        self.imagesink = sink
        self.imagesink.set_xwindow_id(self.window.xid)


    def draw(self, ctx, area):
        # Dibujamos la foto
        ctx.set_line_width(DEF_WIDTH)

        if (self.image != None):
            w = self.image.get_width()
            h = self.image.get_height()
            scale = (1.0 * area.width) / (1.0 * w)
            ctx.scale  (scale, scale)
            ctx.set_source_surface (self.image, 0, 0)
            ctx.paint ()
            ctx.scale  (1/scale, 1/scale)

        #context.set_source_pixbuf(self.pixbuf, area.x, area.y)
        #conext.scale(2,2)
        #context.paint()

        # Dibujamos el recuadro
        ctx.rectangle(area.x, area.y, area.width, area.height)
        if (self.pagina.get_cuadro_activo() == self):
            ctx.set_source_rgb(1, 1, 1)
        else :
            ctx.set_source_rgb(0, 0, 0)
        ctx.stroke() 

        # Por ultimo dibujamos los globos
        self.draw_globos(ctx)

    def draw_globos(self, context):
        if len(self.globos) > 0:
            for g in self.globos:
                g.imprimir(context)

    def keypress(self,key,keyval):
        if self.glob_press:
            self.glob_press.set_texto(key,keyval,self.context,self.get_allocation())
            self.queue_draw()
            #print gtk.gdk.keyval_name(keyval)
        
    def pressing(self, widget, event):
        # si no es el cuadro seleccionado actualmente redibujo este y el anterior seleccionado
        if (self.pagina.get_cuadro_activo() != self):
            self.pagina.set_cuadro_activo(self)

        #Verifica si al pulsar el mouse se hizo sobre algun globo
        if self.glob_press:
            if self.glob_press.is_selec_tam(event.x,event.y):
                self.is_dimension=True
            elif self.glob_press.is_selec_punto(event.x,event.y):
                self.is_punto=True

        if (not self.is_dimension) and not (self.is_punto):
            if self.glob_press:
                #self.glob_press.is_selec(event.x,event.y)
                self.glob_press.no_selec()
                self.glob_press=False

            if self.globos:
                list_aux=self.globos[:]
                list_aux.reverse()
                for i in list_aux:
                    if i.is_selec(event.x,event.y):
                        # i.mover_a(event.x,event.y,self.get_allocation())
                        self.glob_press=i
                        self.globo_activo = i
                        break
                    self.queue_draw()

    def releassing(self, widget, event):
        #Cuando se deja de pulsar el mouse
        #self.glob_press=False
        self.is_dimension=False
        self.is_punto=False
            
    def moving(self, widget, event):
        if self.is_dimension:
            self.glob_press.set_dimension(event.x,event.y,self.get_allocation(),self.context)
            self.queue_draw()
        elif self.is_punto:
            self.glob_press.mover_punto(event.x,event.y,self.get_allocation())
            self.queue_draw()
        elif self.glob_press:
            self.glob_press.mover_a(event.x,event.y,self.get_allocation())
            self.queue_draw()

        
    
