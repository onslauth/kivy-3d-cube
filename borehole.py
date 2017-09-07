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

		# Array to hold all the cube vertices, 3 x 3 x 3 grid,
		# each with 8 vertices, consisting of 3 values ( x, y z )
		self.cube_vertices = np.zeros( shape = ( 27, 8, 3 ), dtype = 'f' )

		# Create a basic cube
		cube = np.zeros( ( 8, 3 ), 'f' )
		i = 0
		for x in ( -1, 1 ):
			for y in ( -1, 1 ):
				for z in ( -1, 1 ):
					cube[ i ] = [ x, y, z ]
					i += 1

		# Shift the cube to the left of the X axis
		# Shift the cube up above the X axis
		# Shift the cube below the Z axis
		# The cubes top right corner should be at ( 0, 0, 0 )
		cube[:,0:1] -= 1
		cube[:,1:2] += 1
		cube[:,2:3] -= 1

		# Create cubes for each position
		index = 0
		for x in ( -2, 0, 2 ):
			c = cube.copy( )
			c[:,0:1] += x

			for y in ( 0, 2, 4 ):
				d = c.copy( )
				d[:,1:2] += y

				for z in ( 0, -2, -4 ):
					e = d.copy( )
					e[:,2:3] += z
					self.cube_vertices[ index ] = e
					index += 1


		# Reshape the cube vertices into 2d array, 216 rows, of 3 columns
		# row = [ x, y, z ]
		self.cube_vertices = self.cube_vertices.reshape( 216, 3 )

		# The indices for each cube
		self.cube_indices = np.zeros( ( 27, 24 ), 'd' )
		cube_indices = np.array( [ 0, 1, 0, 2, 0, 4, 1, 3, 1, 5, 3, 2, 3, 7, 2, 6, 6, 7, 7, 5, 6, 4, 4, 5 ], 'd' )
		self.cube_indices[ 0 ] = cube_indices
		for i in range( 1, 27 ):
			self.cube_indices[ i ] = ( cube_indices + ( i * 8 ) )

		# Flatten the array into a 1d array
		self.cube_indices = self.cube_indices.reshape( 648, )


		# Polar grid
		DIV = 72
		R = 4.0
		H = 0.5

		deg = np.arange( 0, 2.0 * np.pi, 2.0 * np.pi / DIV )
		x = np.cos( deg ) * R
		y = np.sin( deg ) * R
		z = np.ones( DIV, dtype = 'f' )

		grid = np.array( [ x, y, z * 0.0, x, y, z * H ], 'f' ).transpose( ).reshape( DIV * 2, 3 )
		grid[ 1 ][ 2 ] = H * 2

		gridh = np.array( [ y, z * ( -H / 2 ), x, y, z * ( H / 2 ), x ], 'f' ).transpose( ).reshape( DIV * 2, 3 )

		self.polar_vertices_one = grid.flatten( )
		self.polar_indices_one  = np.arange( len( grid ) )

		#first,second = np.split( gridh, 2 )	
		half = int( len( gridh ) / 2 )
		self.polar_vertices_one_h = gridh[ 0:half ].flatten( )
		self.polar_indices_one_h = np.arange( half )

		DIV = 36
		R = 4.01
		H = 0.8

		deg = np.arange( 0, 2.0 * np.pi, 2.0 * np.pi / DIV )
		x = np.cos( deg ) * R
		y = np.sin( deg ) * R
		z = np.ones( DIV, 'f' )
		grid2 = np.array( [ x, y, z * 0.0, x, y, z * H ], 'f' ).transpose( ).reshape( DIV * 2, 3 )

		gridh2 = np.array( [ y, z * ( -H / 2 ), x, y, z * ( H / 2 ), x ], 'f' ).transpose( ).reshape( DIV * 2, 3 )

		self.polar_vertices_two = grid2.flatten( )
		self.polar_indices_two  = np.arange( len( grid2 ) )

		half = int( len( gridh2 ) / 2 )
		self.polar_vertices_two_h = gridh2[ 0:half ].flatten( )
		self.polar_indices_two_h = np.arange( half )


		kw[ 'shader_file' ] = 'shaders.glsl'
		self.canvas = RenderContext( compute_normal_mat = True )
		shader_file = kw.pop( 'shader_file' )
		self.canvas.shader.source = resource_find( shader_file )
		self._touches = [ ]

		super( Renderer, self ).__init__( **kw )

		with self.canvas:
			# This controls the camera position, or rather, shifts the world
			self.translate = Translate( 0, -1, -15 )

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
				     intensity = 0.5 )

			self.cube_mesh = Mesh( vertices = self.cube_vertices.flatten( ),
					       indices = self.cube_indices,
					       fmt = [ ( b'v_pos', 3, 'float' ) ],
					       mode = 'lines' )

			ChangeState( Kd = ( 1.0, 1.0, 1.0 ),
				     Ka = ( 1.0, 1.0, 1.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 0.5 )

			Mesh( vertices = self.polar_vertices_one,
			      indices = self.polar_indices_one,
			      fmt = [ ( b'v_pos', 3, 'float' ) ],
			      mode = 'lines' )

			ChangeState( Kd = ( 1.0, 1.0, 1.0 ),
				     Ka = ( 1.0, 1.0, 1.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 0.8 )

			Mesh( vertices = self.polar_vertices_two,
			      indices = self.polar_indices_two,
			      fmt = [ ( b'v_pos', 3, 'float' ) ],
			      mode = 'lines' )

			ChangeState( Kd = ( 1.0, 1.0, 1.0 ),
				     Ka = ( 1.0, 1.0, 1.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 0.5 )

			Mesh( vertices = self.polar_vertices_one_h,
			      indices = self.polar_indices_one_h,
			      fmt = [ ( b'v_pos', 3, 'float' ) ],
			      mode = 'lines' )


			ChangeState( Kd = ( 1.0, 1.0, 1.0 ),
				     Ka = ( 1.0, 1.0, 1.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 0.8 )
			Mesh( vertices = self.polar_vertices_two_h,
			      indices = self.polar_indices_two_h,
			      fmt = [ ( b'v_pos', 3, 'float' ) ],
			      mode = 'lines' )

		asp = float( Window.width ) / Window.height / 2.0
		proj = Matrix( ).view_clip( -asp, asp, -0.5, 0.5, 1, 100, 1 )
		self.canvas[ 'projection_mat' ] = proj

		Window.request_keyboard( None, self ).bind( on_key_down = self.on_keyboard_down )

	def on_keyboard_down( self, keyboard, keycode, text, modifiers ):

		## This shifts the line
		if keycode[ 1 ] == "up":
			self.translate.y -= 1
		elif keycode[ 1 ] == "down":
			self.translate.y += 1


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
