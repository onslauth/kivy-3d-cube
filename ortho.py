from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics import *
from kivy.core.text import Label as CoreLabel
import numpy as np

def get_borehole_line( ):
	x = np.concatenate( ( np.arange( 0, 30, step = 0.1 ), np.arange( 30, 15, step = -0.05 ) ) )
	y = np.concatenate( ( np.arange( 0, 30, step = 0.1 ), np.arange( 30, 60, step = 0.1 ) ) )
	z = np.concatenate( ( np.arange( 0, -60, step = -0.2 ), np.arange( -60, -120, step = -0.2 ) ) )

	hole = np.column_stack( ( x, y, z ) )

	return hole

class Renderer(Widget):
	SCALE_FACTOR = 0.025
	MAX_SCALE = 5.0
	MIN_SCALE = 0.3
	ROTATE_SPEED = 1.

	POLAR_RADIUS = 4.0
	STEP = 0.1

	def __init__( self, **kw ):
		super( Renderer, self ).__init__( **kw )
	
		self.borehole_vertices = get_borehole_line( )
		self.borehole_indices = [ ]
		for i in range( 0, len( self.borehole_vertices ) - 1 ):
			self.borehole_indices += [ i, i + 1 ]
		#self.borehole_indices  = np.arange( len( self.borehole_vertices ) )
		self.borehole_depth = 0


		# Load the shaders
		kw[ 'shader_file' ] = 'shaders.glsl'
		self.canvas = RenderContext( compute_normal_mat = True )
		shader_file = kw.pop( 'shader_file' )
		self.canvas.shader.source = resource_find( shader_file )
		self._touches = [ ]

		Window.request_keyboard( None, self ).bind( on_key_down = self.on_keyboard_down )

		self.setup_polar_axes( )
		self.setup_scene( )

	def setup_scene( self ):

		with self.canvas:
			# This controls the camera position, or rather, shifts the world
			self.translate = Translate( 0, -1, -15 )

			self.rot = Rotate( 0, 1, 1, 1 )
			self.rotx = Rotate( 0, 1, 0, 0 )
			self.roty = Rotate( 0, 0, 1, 0 )

			# This controls the zoom
			self.scale = Scale( 1 )

			# Draw the borehole line, and put the vertices in a PushMatrix - PopMatrix
			# enclosure so that they can be translated separately

			PushMatrix( )
			self.translate_borehole = Translate( 0, 0, 0 )
			
			ChangeState( Kd = ( 0.0, 1.0, 0.0 ),
				     Ka = ( 1.0, 1.0, 0.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 0.8 )

			Mesh( vertices = self.borehole_vertices.flatten( ),
					       indices = self.borehole_indices,
					       fmt = [ ( b'v_pos', 3, 'float' ) ],
					       mode = 'lines' )
			PopMatrix( )


			# Draw the vertical polar grid
			ChangeState( Kd = ( 1.0, 1.0, 1.0 ),
				     Ka = ( 1.0, 1.0, 1.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 0.5 )

			Mesh( vertices = self.vertical_polar_vertices_one,
			      indices  = self.vertical_polar_indices_one,
			      fmt      = [ ( b'v_pos', 3, 'float' ) ],
			      mode     = 'lines' )

			ChangeState( Kd = ( 1.0, 1.0, 1.0 ),
				     Ka = ( 1.0, 1.0, 1.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 0.8 )

			Mesh( vertices = self.vertical_polar_vertices_two,
			      indices  = self.vertical_polar_indices_two,
			      fmt      = [ ( b'v_pos', 3, 'float' ) ],
			      mode     = 'lines' )



			# Draw the horizontal polar grid
			# This is enclosed in a PushMatrix - PopMatrix so that we can add a separate rotate
			# function to these vertices
			PushMatrix( )

			self.horizontal_polar_rotate = Rotate( 0, 0, 0, 1 )

			self.set_horizontal_polar_grid_angle( )
	
			ChangeState( Kd = ( 1.0, 1.0, 1.0 ),
				     Ka = ( 1.0, 1.0, 1.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 0.5 )

			Mesh( vertices = self.horizontal_polar_vertices_one,
			      indices  = self.horizontal_polar_indices_one,
			      fmt      = [ ( b'v_pos', 3, 'float' ) ],
			      mode     = 'lines' )

			ChangeState( Kd = ( 1.0, 1.0, 1.0 ),
				     Ka = ( 1.0, 1.0, 1.0 ),
				     Ks = ( .3, .3, .3 ),
				     Tr = 1.,
				     Ns = 1.,
				     intensity = 0.8 )

			Mesh( vertices = self.horizontal_polar_vertices_two,
			      indices  = self.horizontal_polar_indices_two,
			      fmt      = [ ( b'v_pos', 3, 'float' ) ],
			      mode     = 'lines' )

			PopMatrix( )


		asp = float( Window.width ) / Window.height / 2.0
		proj = Matrix( ).view_clip( -asp, asp, -0.5, 0.5, 1, 100, 1 )
		self.canvas[ 'projection_mat' ] = proj


	def set_horizontal_polar_grid_angle( self ):
			curr_pos = self.borehole_vertices[ self.borehole_depth ]
			next_pos = self.borehole_vertices[ self.borehole_depth + self.look_ahead ]
			diff = next_pos - curr_pos

			angle = np.arctan2( diff[ 1 ], diff[ 0 ] ) * 180 / np.pi
			self.horizontal_polar_rotate.angle = angle

	def on_keyboard_down( self, keyboard, keycode, text, modifiers ):

		## This shifts the line
		if keycode[ 1 ] == "up":
	
			if self.borehole_depth >= len( self.borehole_vertices ) - self.look_ahead - 1:
				return
			
			current_pos = self.borehole_vertices[ self.borehole_depth ]
			next_pos    = self.borehole_vertices[ self.borehole_depth + 1 ]

			self.set_horizontal_polar_grid_angle( )
			
			self.borehole_depth += 1

			diff = next_pos - current_pos
			self.translate_borehole.xyz -= diff
		elif keycode[ 1 ] == "down":

			if self.borehole_depth <= 0:
				return

			current_pos = self.borehole_vertices[ self.borehole_depth ]
			next_pos    = self.borehole_vertices[ self.borehole_depth - 1 ]

			self.set_horizontal_polar_grid_angle( )

			self.borehole_depth -= 1

			diff = current_pos - next_pos
			self.translate_borehole.xyz += diff

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

	def get_horizontal_polar_grid( self ):
		DIV = 72
		R = 4.0
		H = 0.5

		deg = np.arange( 0, 2.0 * np.pi, 2.0 * np.pi / DIV )
		x = np.cos( deg ) * R
		y = np.sin( deg ) * R
		z = np.ones( DIV, dtype = 'f' )

		gridh = np.array( [ y, z * ( -H / 2 ), x, y, z * ( H / 2 ), x ], 'f' ).transpose( ).reshape( DIV * 2, 3 )

		DIV = 36
		R = 4.01
		H = 0.8

		deg = np.arange( 0, 2.0 * np.pi, 2.0 * np.pi / DIV )
		x = np.cos( deg ) * R
		y = np.sin( deg ) * R
		z = np.ones( DIV, 'f' )

		gridh2 = np.array( [ y, z * ( -H / 2 ), x, y, z * ( H / 2 ), x ], 'f' ).transpose( ).reshape( DIV * 2, 3 )

		return ( gridh, gridh2 )

	def get_vertical_polar_grid( self ):
		DIV = 72
		R = self.POLAR_RADIUS
		H = 0.5

		deg = np.arange( 0, 2.0 * np.pi, 2.0 * np.pi / DIV )
		x = np.cos( deg ) * R
		y = np.sin( deg ) * R
		z = np.ones( DIV, dtype = 'f' )

		grid = np.array( [ x, y, z * 0.0, x, y, z * H ], 'f' ).transpose( ).reshape( DIV * 2, 3 )
		grid[ 1 ][ 2 ] = H * 2

		DIV = 36
		R = self.POLAR_RADIUS + 0.01
		H = 0.8

		deg = np.arange( 0, 2.0 * np.pi, 2.0 * np.pi / DIV )
		x = np.cos( deg ) * R
		y = np.sin( deg ) * R
		z = np.ones( DIV, 'f' )
		grid2 = np.array( [ x, y, z * 0.0, x, y, z * H ], 'f' ).transpose( ).reshape( DIV * 2, 3 )

		return ( grid, grid2 )

	def setup_polar_axes( self ):

		# Get the vertices for the vertical polar grid
		vertical_polar_grid = self.get_vertical_polar_grid( )

		grid = vertical_polar_grid[ 0 ]
		self.vertical_polar_vertices_one = grid.flatten( )
		self.vertical_polar_indices_one  = np.arange( len( grid ) )

		grid = vertical_polar_grid[ 1 ]
		self.vertical_polar_vertices_two = grid.flatten( )
		self.vertical_polar_indices_two  = np.arange( len( grid ) )

		
		# Get the vertices for the horizontal polar grid
		horizontal_polar_grid = self.get_horizontal_polar_grid( )

		grid = horizontal_polar_grid[ 0 ]
		half = int( len( grid ) / 2 ) + 2
		self.horizontal_polar_vertices_one = grid[ 0:half ].flatten( )
		self.horizontal_polar_indices_one  = np.arange( half )

		grid = horizontal_polar_grid[ 1 ]
		half = int( len( grid ) / 2 ) + 2
		self.horizontal_polar_vertices_two = grid[ 0:half ].flatten( )
		self.horizontal_polar_indices_two  = np.arange( half )

		# Calculate the coordinate that the horizontal polar grid
		# should be set to in the borehole vertices
		self.look_ahead = int( self.POLAR_RADIUS / self.STEP / 2 )

class MyApp(App):
	def build( self ):
		return Renderer( )

if __name__ == '__main__':
	MyApp( ).run( )
