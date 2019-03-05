import serial
from state import State
from Sender import Sender_Driver
# from Receiver import Receiver_Driver


# Start Of Our States
class Receiver(State):
	"""
	The state indicating that the driver/arduino is
	going to receive data.
	"""
	def on_event(self, event):
		if event == 'send':
			return Sender()
		elif event == '':
			return Meta_Parser()
			
		return self


class Meta_Parser(State):
	"""
	The state indicating that we are parsing the
	meta packet.
	"""
	def on_event(self, event):
		if event == '':
			return Receive_Data()
			
		return self


class Receive_Data(State):
	"""
	The state indicating that we are currently
	receiving data.
	"""
	def on_event(self, event):
		if event == 'timeout':
			return Receiver()
		elif event == 'finish':
			return Receiver()
		elif event == 'resend':
			return Receive_Data()
		elif event == '':
			return Receive_Data()
			
		return self


class Sender(State):
	"""
	The state indicating that the driver/arduino is
	going to send data.
	"""
	def on_event(self, event):
		if event == '':
			return Create_Meta()
			
		return self


class Create_Meta(State):
	"""
	The state indicating that we are creating the
	meta data packet.
	"""
        
	def on_event(self, event):
		if event == '':
			return Send_Data()
			
		return self

	# TODO: Get file_name and serialPort from LiFiGUI
	# sd = Sender_Driver("..\\files\\sender_test.txt", serial.Serial())
	# sd.meta_creator()


class Send_Data(State):
	"""
	The state indicating that we are currently
	receiving data.
	"""
	def on_event(self, event):
		if event == '':
			return Wait()
			
		return self

	# TODO: Get file_name and serialPort from LiFiGUI
	# sd = Sender_Driver("..\\files\\sender_test.txt", serial.Serial())
	# sd.packet_loop()


class Wait(State):
	"""
	The state indicating that we are currently
	waiting on a command.
	"""
	def on_event(self, event):
		if event == 'timeout':
			return Receiver()
		elif event == 'finish':
			return Receiver()
		elif event == 'resend':
			return Send_Data()
		elif event == '':
			return Wait()
			
		return self
		
# End Of Our States
