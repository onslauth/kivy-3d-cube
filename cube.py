from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics import *
import numpy as np

class Renderer(Widget):
	SCALE_FACTOR = 0.025
	MAX_SCALE = 3.0
	MIN_SCALE = 0.3
	ROTATE_SPEED = 1.

	def __init__( self, **kw ):

		self.vertices = [ ]

		cube = np.zeros( ( 8, 3 ), 'f' )
		i = 0
		for x in ( -1, 1 ):
			for y in ( -1, 1 ):
				for z in ( -1, 1 ):
					cube[ i ] = [ x, y, z ]
					i += 1

		# Shift the cube down below the x-axis
		cube[:,1:2] -= 1

		# Create cubes for each position
		for x in ( -2, 0, 2 ):
			c = cube.copy( )
			c[:,0:1] += x
			self.vertices.append( c.flatten( ) )

			for y in ( 0, -2, -4 ):
				d = c.copy( )
				d[:,1:2] += y
				self.vertices.append( d.flatten( ) )

				for z in ( -2, 0, 2 ):
					e = d.copy( )
					e[:,2:3] += z
					self.vertices.append( e.flatten( ) )

		# The indices for each cube
		self.indices = [ 0, 1, 0, 2, 0, 4, 1, 3, 1, 5, 3, 2, 3, 7, 2, 6, 6, 7, 7, 5, 6, 4, 4, 5 ]


		kw[ 'shader_file' ] = 'shaders.glsl'
		self.canvas = RenderContext( compute_normal_mat = True )
		shader_file = kw.pop( 'shader_file' )
		self.canvas.shader.source = resource_find( shader_file )
		self._touches = [ ]

		super( Renderer, self ).__init__( **kw )

		with self.canvas:
			# This controls the camera position, or rather, shifts the world
			Translate( 0, -1, -10 )

			self.rot = Rotate( 0, 1, 1, 1 )
			self.rotx = Rotate( 0, 1, 0, 0 )
			self.roty = Rotate( 0, 0, 1, 0 )

			# This controls the zoom
			self.scale = Scale( 1 )

			ChangeState( Kd = ( 1.0, 0.0, 0.0 ),
				     Ka = ( 1.0, 1.0, 0.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 1. )

			# Draw the vertices and indices
			for i in range( len( self.vertices ) ):
				Mesh( vertices = self.vertices[ i ],
				      indices = self.indices,
				      fmt = [ ( b'v_pos', 3, 'float' ) ],
				      mode = 'lines' )

		asp = float( Window.width ) / Window.height / 2.0
		proj = Matrix( ).view_clip( -asp, asp, -0.5, 0.5, 1, 100, 1 )
		self.canvas[ 'projection_mat' ] = proj

		Window.request_keyboard( None, self ).bind( on_key_down = self.on_keyboard_down )

	def on_keyboard_down( self, keyboard, keycode, text, modifiers ):
		if keycode[ 1 ] == "left": self.rot.angle -= 10
		elif keycode[ 1 ] == "right": self.rot.angle += 10

	def ignore_undertouch( func ):
		def wrap( self, touch ):
			gl = touch.grab_list
			if len( gl ) == 0 or ( self is gl[ 0 ]( ) ):
				return func( self, touch )
		return wrap

	@ignore_undertouch
	def on_touch_down( self, touch ):
		touch.grab( self )
		self._touches.append( touch )

		if 'button' in touch.profile and touch.button in ( 'scrollup', 'scrolldown' ):

			if touch.button == "scrolldown":
				scale = self.SCALE_FACTOR

			if touch.button == "scrollup":
				scale = -self.SCALE_FACTOR

			xyz = self.scale.xyz
			scale = xyz[ 0 ] + scale
			if scale < self.MAX_SCALE and scale > self.MIN_SCALE:
				self.scale.xyz = ( scale, scale, scale )

	@ignore_undertouch
	def on_touch_up( self, touch ):
		touch.ungrab( self )
		if touch in self._touches:
			self._touches.remove( touch )

	def define_rotate_angle(self, touch):
		x_angle = (touch.dx/self.width)*360.*self.ROTATE_SPEED
		y_angle = -1*(touch.dy/self.height)*360.*self.ROTATE_SPEED

		return x_angle, y_angle

	@ignore_undertouch
	def on_touch_move( self, touch ):
		if touch in self._touches and touch.grab_current == self:
			if len(self._touches) == 1:
			# here do just rotation        
				ax, ay = self.define_rotate_angle(touch)

				self.roty.angle += ax
				self.rotx.angle += ay


class MyApp(App):
	def build( self ):
		return Renderer( )

if __name__ == '__main__':
	MyApp( ).run( )
