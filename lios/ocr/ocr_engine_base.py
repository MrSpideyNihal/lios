#! /usr/bin/python3 
###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2015-2016 Nalin.x.Linux GPL-3
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

import abc
import multiprocessing


class OcrEngineBase(metaclass=abc.ABCMeta):
	def __init__(self,language=None):
		self.language = language
	
	@staticmethod
	@abc.abstractmethod
	def get_available_languages():
		return

	@staticmethod
	@abc.abstractmethod
	def support_multiple_languages():
		return
	
	@abc.abstractmethod
	def ocr_image_to_text(self,image_file_name):
		pass
	
	def cancel():
		pass
		

	def set_language(self,language):
		if language in self.__class__.get_available_languages():
			self.language = language
			return True
		else:
			return False

	def set_language_2(self,language):
		if language in self.__class__.get_available_languages():
			self.language_2 = language
			return True
		else:
			self.language_2 = False
			return False

	def set_language_3(self,language):
		if language in self.__class__.get_available_languages():
			self.language_3 = language
			return True
		else:
			self.language_3 = False
			return False
	
	def ocr_image_to_text_with_multiprocessing(self,image_file_name):
		# Call directly instead of multiprocessing to avoid pickling issues
		# Python 3.14's forkserver can't pickle lambdas that capture 'self'
		return self.ocr_image_to_text(image_file_name)


	@staticmethod
	@abc.abstractmethod
	def is_available():
		return		
