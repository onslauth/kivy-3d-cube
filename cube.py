from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics import *
from kivy.core.text import Label as CoreLabel
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
		cube[:,0:1] -= 1
		cube[:,1:2] += 1
		cube[:,2:3] -= 1

		# Create cubes for each position
		for x in ( -2, 0, 2 ):
			c = cube.copy( )
			c[:,0:1] += x
			self.vertices.append( c.flatten( ) )

			for y in ( 0, 2, 4 ):
				d = c.copy( )
				d[:,1:2] += y
				self.vertices.append( d.flatten( ) )

				for z in ( 0, -2, -4 ):
					e = d.copy( )
					e[:,2:3] += z
					self.vertices.append( e.flatten( ) )

		# The indices for each cube
		self.indices = [ 0, 1, 0, 2, 0, 4, 1, 3, 1, 5, 3, 2, 3, 7, 2, 6, 6, 7, 7, 5, 6, 4, 4, 5 ]

		self.line_vertices = np.array( [ [ 0.000000, 0.000000, 0.000000 ],
				       	         [ 0.000000, 0.999998, -0.001745 ],
				       	         [ 0.000000, 1.999997, -0.003491 ],
				       	         [ 0.000000, 2.999995, -0.005236 ],
				       	         [ 0.000000, 3.999994, -0.006981 ],
				       	         [ 0.000000, 4.999992, -0.008727 ],
				       	         [ 0.000000, 5.999991, -0.010472 ],
				       	         [ 0.000000, 6.999989, -0.012217 ],
				       	         [ 0.000000, 7.999988, -0.013963 ],
				       	         [ 0.000000, 8.999986, -0.015708 ],
				       	         [ 0.000000, 9.999985, -0.017453 ],
				       	         [ 0.000000, 10.999983, -0.019199 ],
				       	         [ 0.000000, 11.999982, -0.020944 ],
				       	         [ 0.000000, 12.999980, -0.022689 ],
				       	         [ 0.000000, 13.999979, -0.024435 ],
				       	         [ 0.000000, 14.999977, -0.026180 ],
				       	         [ 0.000000, 15.999976, -0.027925 ],
				       	         [ 0.000000, 16.999974, -0.029671 ],
				       	         [ 0.000000, 17.999973, -0.031416 ],
				       	         [ 0.000000, 18.999971, -0.033161 ],
				       	         [ 0.000000, 19.999970, -0.034907 ],
				       	         [ 0.000000, 20.999968, -0.036652 ],
				       	         [ 0.000000, 21.999966, -0.038397 ],
				       	         [ 0.000000, 22.999965, -0.040143 ],
				       	         [ 0.000000, 23.999963, -0.041888 ],
				       	         [ 0.000000, 24.999962, -0.043633 ],
				       	         [ 0.000000, 25.999960, -0.045379 ],
				       	         [ 0.000000, 26.999959, -0.047124 ],
				       	         [ 0.000000, 27.999957, -0.048869 ],
				       	         [ 0.000000, 28.999956, -0.050615 ],
				       	         [ 0.000000, 29.999954, -0.052360 ],
				       	         [ 0.000000, 30.999953, -0.054105 ],
				       	         [ 0.000000, 31.999951, -0.055851 ],
				       	         [ 0.000000, 32.999950, -0.057596 ],
				       	         [ 0.000000, 33.999948, -0.059341 ],
				       	         [ 0.000000, 34.999947, -0.061086 ],
				       	         [ 0.000000, 35.999945, -0.062832 ],
				       	         [ 0.000000, 36.999944, -0.064577 ],
				       	         [ 0.000000, 37.999942, -0.066322 ],
				       	         [ 0.000000, 38.999941, -0.068068 ],
				       	         [ 0.000000, 39.999939, -0.069813 ],
				       	         [ 0.000000, 40.999938, -0.071558 ],
				       	         [ 0.000000, 41.999936, -0.073304 ],
				       	         [ 0.000000, 42.999935, -0.075049 ],
				       	         [ 0.000000, 43.999933, -0.076794 ],
				       	         [ 0.000000, 44.999931, -0.078540 ],
				       	         [ 0.000000, 45.999930, -0.080285 ],
				       	         [ 0.000000, 46.999928, -0.082030 ],
				       	         [ 0.000000, 47.999927, -0.083776 ],
				       	         [ 0.000000, 48.999925, -0.085521 ],
				       	         [ 0.000000, 49.999924, -0.087266 ],
				       	         [ 0.000000, 50.999922, -0.089012 ],
				       	         [ 0.000000, 51.999921, -0.090757 ],
				       	         [ 0.000000, 52.999919, -0.092502 ],
				       	         [ 0.000000, 53.999918, -0.094248 ],
				       	         [ 0.000000, 54.999916, -0.095993 ],
				       	         [ 0.000000, 55.999915, -0.097738 ],
				       	         [ 0.000000, 56.999913, -0.099484 ],
				       	         [ 0.000000, 57.999912, -0.101229 ],
				       	         [ 0.000000, 58.999910, -0.102974 ],
				       	         [ 0.000000, 59.999909, -0.104720 ],
				       	         [ 0.000000, 60.999907, -0.106465 ],
				       	         [ 0.000000, 61.999906, -0.108210 ],
				       	         [ 0.000000, 62.999904, -0.109956 ],
				       	         [ 0.000000, 63.999903, -0.111701 ],
				       	         [ 0.000000, 64.999901, -0.113446 ],
				       	         [ 0.000000, 65.999899, -0.115192 ],
				       	         [ 0.000000, 66.999898, -0.116937 ],
				       	         [ 0.000000, 67.999896, -0.118682 ],
				       	         [ 0.000000, 68.999895, -0.120428 ],
				       	         [ 0.000000, 69.999893, -0.122173 ],
				       	         [ 0.000000, 70.999892, -0.123918 ],
				       	         [ 0.000000, 71.999890, -0.125664 ],
				       	         [ 0.000000, 72.999889, -0.127409 ],
				       	         [ 0.000000, 73.999887, -0.129154 ],
				       	         [ 0.000000, 74.999886, -0.130900 ],
				       	         [ 0.000000, 75.999884, -0.132645 ],
				       	         [ 0.000000, 76.999883, -0.134390 ],
				       	         [ 0.000000, 77.999881, -0.136136 ],
				       	         [ 0.000000, 78.999880, -0.137881 ],
				       	         [ 0.000000, 79.999878, -0.139626 ],
				       	         [ 0.000000, 80.999877, -0.141372 ],
				       	         [ 0.000000, 81.999875, -0.143117 ],
				       	         [ 0.000000, 82.999874, -0.144862 ],
				       	         [ 0.000000, 83.999872, -0.146608 ],
				       	         [ 0.000000, 84.999871, -0.148353 ],
				       	         [ 0.000000, 85.999869, -0.150098 ],
				       	         [ 0.000000, 86.999867, -0.151844 ],
				       	         [ 0.000000, 87.999866, -0.153589 ],
				       	         [ 0.000000, 88.999864, -0.155334 ],
				       	         [ 0.000000, 89.999863, -0.157080 ],
				       	         [ 0.000000, 90.999861, -0.158825 ],
				       	         [ 0.000000, 91.999860, -0.160570 ],
				       	         [ 0.000000, 92.999858, -0.162316 ],
				       	         [ 0.000000, 93.999857, -0.164061 ],
				       	         [ 0.000000, 94.999855, -0.165806 ],
				       	         [ 0.000000, 95.999854, -0.167552 ],
				       	         [ 0.000000, 96.999852, -0.169297 ],
				       	         [ 0.000000, 97.999851, -0.171042 ],
				       	         [ 0.000000, 98.999849, -0.172788 ],
				       	         [ 0.000000, 99.999848, -0.174533 ],
				       	         [ 0.000000, 100.999846, -0.176278 ],
				       	         [ 0.000000, 101.999845, -0.178023 ],
				       	         [ 0.000000, 102.999843, -0.179769 ],
				       	         [ 0.000000, 103.999842, -0.181514 ],
				       	         [ 0.000000, 104.999840, -0.183259 ],
				       	         [ 0.000000, 105.999839, -0.185005 ],
				       	         [ 0.000000, 106.999837, -0.186750 ],
				       	         [ 0.000000, 107.999836, -0.188495 ],
				       	         [ 0.000000, 108.999834, -0.190241 ],
				       	         [ 0.000000, 109.999832, -0.191986 ],
				       	         [ 0.000000, 110.999831, -0.193731 ],
				       	         [ 0.000000, 111.999829, -0.195477 ],
				       	         [ 0.000000, 112.999828, -0.197222 ],
				       	         [ 0.000000, 113.999826, -0.198967 ],
				       	         [ 0.000000, 114.999825, -0.200713 ],
				       	         [ 0.000000, 115.999823, -0.202458 ],
				       	         [ 0.000000, 116.999822, -0.204203 ],
				       	         [ 0.000000, 117.999820, -0.205949 ],
				       	         [ 0.000000, 118.999819, -0.207694 ],
				       	         [ 0.000000, 119.999817, -0.209439 ],
				       	         [ 0.000000, 120.999816, -0.211185 ],
				       	         [ 0.000000, 121.999814, -0.212930 ],
				       	         [ 0.000000, 122.999813, -0.214675 ] ] )

		print( self.line_vertices[ 0 ] )
		print( self.line_vertices.shape )

		self.line_indices = [ ]
		for i in range( 0, len( self.line_vertices ) ):
			self.line_indices += [ i, i + 1 ]

		kw[ 'shader_file' ] = 'shaders.glsl'
		self.canvas = RenderContext( compute_normal_mat = True )
		shader_file = kw.pop( 'shader_file' )
		self.canvas.shader.source = resource_find( shader_file )
		self._touches = [ ]

		super( Renderer, self ).__init__( **kw )

		with self.canvas:
			# This controls the camera position, or rather, shifts the world
			Translate( 0, -1, -15 )

			self.rot = Rotate( 0, 1, 1, 1 )
			self.rotx = Rotate( 0, 1, 0, 0 )
			self.roty = Rotate( 0, 0, 1, 0 )

			# This controls the zoom
			self.scale = Scale( 1 )

			# Change the colour of the mesh to red.
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

			# Change the details of the line, i.e. colour to green
			ChangeState( Kd = ( 0.0, 1.0, 0.0 ),
				     Ka = ( 1.0, 1.0, 0.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 1. )

			# Draw the line
			Mesh( vertices = self.line_vertices.flatten( ),
			      indices = self.line_indices,
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
