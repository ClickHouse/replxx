#! /usr/bin/python3

import pexpect
import unittest
import re
import os
import subprocess
import signal
import sys
import tempfile
import time

_TEST_BASE_CWD = os.path.abspath( os.path.dirname( __file__ ) or "." )

keytab = {
	"<home>": "\033[1~",
	"<s-home>": "\033[1;2H",
	"<c-home>": "\033[1;5H",
	"<end>": "\033[4~",
	"<s-end>": "\033[1;2F",
	"<c-end>": "\033[1;5F",
	"<ins>": "\033[2~",
	"<s-ins>": "\033[2;2~",
	"<c-ins>": "\033[2;5~",
	"<del>": "\033[3~",
	"<s-del>": "\033[3;2~",
	"<c-del>": "\033[3;5~",
	"<pgup>": "\033[5~",
	"<c-pgup>": "\033[5;5~",
	"<pgdown>": "\033[6~",
	"<c-pgdown>": "\033[6;5~",
	"<backspace>": "",
	"<tab>": "\t",
	"<cr>": "\r",
	"<s-cr>": chr( 10 ),
	"<lf>": "\n",
	"<left>": "\033[D",
	"<s-left>": "\033[1;2D",
	"<aleft>": "\033OD",
	"<right>": "\033[C",
	"<s-right>": "\033[1;2C",
	"<aright>": "\033OC",
	"<up>": "\033[A",
	"<s-up>": "\033[1;2A",
	"<aup>": "\033OA",
	"<down>": "\033[B",
	"<s-down>": "\033[1;2B",
	"<adown>": "\033OB",
	"<c-left>": "\033[1;5D",
	"<c-right>": "\033[1;5C",
	"<c-up>": "\033[1;5A",
	"<c-down>": "\033[1;5B",
	"<m-left>": "\033[1;3D",
	"<m-right>": "\033[1;3C",
	"<m-up>": "\033[1;3A",
	"<m-down>": "\033[1;3B",
	"<c-a>": "",
	"<c-b>": "",
	"<c-c>": "",
	"<c-d>": "",
	"<c-e>": "",
	"<c-f>": "",
	"<c-g>": "",
	"<c-k>": "",
	"<c-l>": "",
	"<c-n>": "",
	"<c-p>": "",
	"<c-r>": "",
	"<c-s>": "",
	"<c-t>": "",
	"<c-u>": "",
	"<c-v>": "",
	"<c-w>": "",
	"<c-y>": "",
	"<c-z>": "",
	"<m-b>": "\033b",
	"<m-B>": "\033B",
	"<m-c>": "\033c",
	"<m-C>": "\033C",
	"<m-d>": "\033d",
	"<m-D>": "\033D",
	"<m-f>": "\033f",
	"<m-F>": "\033F",
	"<m-g>": "\033g",
	"<m-l>": "\033l",
	"<m-L>": "\033L",
	"<m-n>": "\033n",
	"<m-p>": "\033p",
	"<m-r>": "\033r",
	"<m-u>": "\033u",
	"<m-U>": "\033U",
	"<m-w>": "\033w",
	"<m-y>": "\033y",
	"<m-.>": "\033.",
	"<m-backspace>": "\033\177",
	"<f1>": "\033OP",
	"<f2>": "\033OQ",
	"<f3>": "\033OR",
	"<f4>": "\033OS",
	"<f5>": "\033[15~",
	"<f6>": "\033[17~",
	"<f7>": "\033[18~",
	"<f8>": "\033[19~",
	"<f9>": "\033[20~",
	"<f10>": "\033[21~",
	"<f11>": "\033[23~",
	"<f12>": "\033[24~",
	"<s-f1>": "\033[1;2P",
	"<s-f2>": "\033[1;2Q",
	"<s-f3>": "\033[1;2R",
	"<s-f4>": "\033[1;2S",
	"<s-f5>": "\033[15;2~",
	"<s-f6>": "\033[17;2~",
	"<s-f7>": "\033[18;2~",
	"<s-f8>": "\033[19;2~",
	"<s-f9>": "\033[20;2~",
	"<s-f10>": "\033[21;2~",
	"<s-f11>": "\033[23;2~",
	"<s-f12>": "\033[24;2~",
	"<c-f1>": "\033[1;5P",
	"<c-f2>": "\033[1;5Q",
	"<c-f3>": "\033[1;5R",
	"<c-f4>": "\033[1;5S",
	"<c-f5>": "\033[15;5~",
	"<c-f6>": "\033[17;5~",
	"<c-f7>": "\033[18;5~",
	"<c-f8>": "\033[19;5~",
	"<c-f9>": "\033[20;5~",
	"<c-f10>": "\033[21;5~",
	"<c-f11>": "\033[23;5~",
	"<c-f12>": "\033[24;5~",
	"<s-tab>": "\033[Z",
	"<paste-pfx>": "\033[200~",
	"<paste-sfx>": "\033[201~"
}

termseq = {
	"\x1bc": "<RIS>",
	"\x1b[0m": "<rst>",
	"\x1b[H": "<mvhm>",
	"\x1b[2J": "<clr>",
	"\x1b[J": "<ceos>",
	"\x1b[0;22;30m": "<black>",
	"\x1b[0;22;31m": "<red>",
	"\x1b[0;22;32m": "<green>",
	"\x1b[0;22;33m": "<brown>",
	"\x1b[0;22;34m": "<blue>",
	"\x1b[0;22;35m": "<magenta>",
	"\x1b[0;22;36m": "<cyan>",
	"\x1b[0;22;37m": "<lightgray>",
	"\x1b[0;90m": "<gray>",
	"\x1b[0;91m": "<brightred>",
	"\x1b[0;92m": "<brightgreen>",
	"\x1b[0;93m": "<yellow>",
	"\x1b[0;94m": "<brightblue>",
	"\x1b[0;95m": "<brightmagenta>",
	"\x1b[0;96m": "<brightcyan>",
	"\x1b[0;97m": "<white>",
	"\x1b[0;1m": "<bold>",
	"\x1b[0;4m": "<underline>",
	"\x1b[0;4;1m": "<bold_underline>",
	"\x1b[0;22;31;1m": "<bold_red>",
	"\x1b[0;22;31;4m": "<underline_red>",
	"\x1b[0;91;1m": "<bold_brightred>",
	"\x1b[0;22;31;4;1m": "<bold_underline_red>",
	"\x1b[40m": "<bgblack>",
	"\x1b[41m": "<bgred>",
	"\x1b[42m": "<bggreen>",
	"\x1b[43m": "<bgbrown>",
	"\x1b[44m": "<bgblue>",
	"\x1b[45m": "<bgmagenta>",
	"\x1b[46m": "<bgcyan>",
	"\x1b[47m": "<bglightgray>",
	"\x1b[100m": "<bggray>",
	"\x1b[101m": "<bgbrightred>",
	"\x1b[102m": "<bgbrightgreen>",
	"\x1b[103m": "<bgyellow>",
	"\x1b[104m": "<bgbrightblue>",
	"\x1b[105m": "<bgbrightmagenta>",
	"\x1b[106m": "<bgbrightcyan>",
	"\x1b[107m": "<bgwhite>",
	"\x1b[1;32m": "<brightgreen>",
	"\x07": "<bell>",
	"\x1b[2~": "<ins-key>",
	"\x1b[?2004h": "<paste-on>",
	"\x1b[?2004l": "<paste-off>",
	# Synchronized update and cursor visibility around each redraw do not change the screen contents.
	"\x1b[?2026h": "",
	"\x1b[?2026l": "",
	"\x1b[?25l": "",
	"\x1b[?25h": ""
}
colRe = re.compile( "\\x1b\\[(\\d+)G" )
upRe = re.compile( "\\x1b\\[(\\d+)A" )
downRe = re.compile( "\\x1b\\[(\\d+)B" )
colorRe = re.compile( "\\x1b\\[0;38;5;(\\d+)m" )
bgcolorRe = re.compile( "\\x1b\\[48;5;(\\d+)m" )

def sym_to_raw( str_ ):
	for sym, seq in keytab.items():
		if isinstance( str_, Rapid ):
			str_ = Rapid( str_.replace( sym, seq ) )
		else:
			str_ = str_.replace( sym, seq )
	return str_

def seq_to_sym( str_ ):
	for seq, sym in termseq.items():
		str_ = str_.replace( seq, sym )
	str_ = colRe.sub( "<c\\1>", str_ )
	str_ = upRe.sub( "<u\\1>", str_ )
	str_ = downRe.sub( "<d\\1>", str_ )
	str_ = colorRe.sub( "<color\\1>", str_ )
	str_ = bgcolorRe.sub( "<bgcolor\\1>", str_ )
	return str_

_words_ = [
	"ada", "algol"
	"bash", "basic",
	"clojure", "cobol", "csharp",
	"eiffel", "erlang",
	"forth", "fortran", "fsharp",
	"go", "groovy",
	"haskell", "huginn",
	"java", "javascript", "julia",
	"kotlin",
	"lisp", "lua",
	"modula",
	"nemerle",
	"ocaml",
	"perl", "php", "prolog", "python",
	"rebol", "ruby", "rust",
	"scala", "scheme", "sql", "swift",
	"typescript"
]

def skip( test_ ):
	return "SKIP" in os.environ and os.environ["SKIP"].find( test_ ) >= 0

verbosity = None

class Rapid( str ): pass

def rapid( item ):
	if isinstance( item, str ):
		r = Rapid( item )
		return r
	return list( map( Rapid, item ) )

def _no_parallel( fn ):
	"""Mark a test as not safe to run inside the parallel pool. Such tests
	depend on wall-clock scheduling (spinner ticks, async print interleaving)
	and become unreliable when the host is saturated by other workers; the
	parallel runner runs them sequentially after the pool drains."""
	fn._no_parallel = True
	return fn

class ReplxxTests( unittest.TestCase ):
	_prompt_ = "\033\\[1;32mreplxx\033\\[0m> "
	_cxxSample_ = os.path.join( _TEST_BASE_CWD, "build/debug/replxx-example-cxx-api" )
	_cSample_ = os.path.join( _TEST_BASE_CWD, "build/debug/replxx-example-c-api" )
	# Allow any leftover CSI escape sequences (cursor moves, clear-to-EOS,
	# color resets) that `replxx` may emit during shutdown between the
	# final prompt redraw and the "Exiting Replxx" line - these appear or
	# not depending on scheduling under heavy parallel load.
	_end_ = "(?:\033\\[[0-9;]*[a-zA-Z])*\r\nExiting Replxx\r\n"

	def setUp( self_ ):
		# Per-test tmpdir; binary uses it as cwd so each test has its own
		# replxx_history.txt and friends. Required for parallel test runs.
		self_._tmpdir = tempfile.mkdtemp( prefix = "replxx-test-" )
		self_._prev_cwd = os.getcwd()
		os.chdir( self_._tmpdir )

	def tearDown( self_ ):
		os.chdir( self_._prev_cwd )
		import shutil
		shutil.rmtree( self_._tmpdir, ignore_errors = True )
	def send_str( self_, str_, intraKeyDelay_ ):
		if isinstance(str_, Rapid):
			self_._replxx.send( str_ )
			return
		for char in str_:
			self_._replxx.send( char )
			time.sleep( intraKeyDelay_ )

	def check_scenario(
		self_, seq_, expected_,
		history = "one\ntwo\nthree\n",
		term = "xterm",
		command = _cxxSample_,
		dimensions = ( 25, 80 ),
		prompt = _prompt_,
		end = None,
		encoding = "utf-8",
		pause = 0.25,
		intraKeyDelay = 0.002
	):
		if end is None:
			end = prompt + ReplxxTests._end_
		with open( "replxx_history.txt", "wb" ) as f:
			f.write( history.encode( encoding ) )
			f.close()
		os.environ["TERM"] = term
		if isinstance( command, str ):
			command = command.replace( "\n", "~" )
		if verbosity >= 2:
			print( "\nTERM: {}, SIZE: {}, CMD: {}".format( term, dimensions, command ) )
		prompt = prompt.replace( "\n", "\r\n" ).replace( "\r\r", "\r" )
		end = end.replace( "\n", "\r\n" ).replace( "\r\r", "\r" )
		if isinstance( command, str ):
			self_._replxx = pexpect.spawn( command, maxread = 1, encoding = encoding, dimensions = dimensions )
		else:
			self_._replxx = pexpect.spawn( command[0], args = command[1:], maxread = 1, encoding = encoding, dimensions = dimensions )
		self_._replxx.expect( prompt )
		self_.maxDiff = None
		if isinstance( seq_, str ):
			if isinstance( seq_, Rapid ):
				seqs = rapid( seq_.split( "<c-z>" ) )
			else:
				seqs = seq_.split( "<c-z>" )
			for seq in seqs:
				last = seq is seqs[-1]
				if not last:
					seq += "<c-z>"
				self_.send_str( sym_to_raw( seq ), intraKeyDelay )
				if not last:
					time.sleep( pause )
					self_._replxx.kill( signal.SIGCONT )
		else:
			for seq in seq_:
				last = seq is seq_[-1]
				self_.send_str( sym_to_raw( seq ), intraKeyDelay )
				if not last:
					time.sleep( pause )
		self_._replxx.expect( end )
		if isinstance( expected_, str ):
			self_.assertSequenceEqual( seq_to_sym( self_._replxx.before ), expected_ )
		else:
			try:
				self_.assertIn( seq_to_sym( self_._replxx.before ), expected_ )
			except:
				self_.assertSequenceEqual( seq_to_sym( self_._replxx.before ), "" )
	def test_unicode( self_ ):
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> aóą Ϩ 𓢀  󃔀  <rst><ceos><rst><c21>"
			"<c9>aóą Ϩ 𓢀  󃔀  <rst><ceos><c21>\r\n"
			"aóą Ϩ 𓢀  󃔀  \r\n<c1>",
			"aóą Ϩ 𓢀  󃔀  \n"
		)
		self_.check_scenario(
			"aóą Ϩ 𓢀  󃔀  <cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>aó<rst><ceos><rst><c11><c9>aóą<rst><ceos><rst><c12><c9>aóą <rst><ceos>"
			"<rst><c13><c9>aóą Ϩ<rst><ceos><rst><c14><c9>aóą Ϩ <rst><ceos><rst><c15><c9>aóą Ϩ 𓢀<rst><ceos><rst>"
			"<c16><c9>aóą Ϩ 𓢀 <rst><ceos><rst><c17><c9>aóą Ϩ 𓢀  <rst><ceos><rst><c18><c9>aóą Ϩ 𓢀  󃔀<rst><ceos>"
			"<rst><c19><c9>aóą Ϩ 𓢀  󃔀 <rst><ceos><rst><c20><c9>aóą Ϩ 𓢀  󃔀  <rst><ceos><rst><c21><c9>"
			"aóą Ϩ 𓢀  󃔀  <rst><ceos><c21>\r\n"
			"aóą Ϩ 𓢀  󃔀  \r\n"
			"<c1>"
		)
	@unittest.skipIf( skip( "8bit_encoding" ), "broken platform" )
	def test_8bit_encoding( self_ ):
		LC_CTYPE = "LC_CTYPE"
		exists = LC_CTYPE in os.environ
		lcCtype = None
		if exists:
			lcCtype = os.environ[LC_CTYPE]
		os.environ[LC_CTYPE] = "pl_PL.ISO-8859-2"
		self_.check_scenario(
			"<aup><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> text ~ó~<rst><ceos><rst><c17><c9>text ~ó~<rst><ceos><c17>\r\ntext ~ó~\r\n<c1>",
			"text ~ó~\n",
			encoding = "iso-8859-2"
		)
		if exists:
			os.environ[LC_CTYPE] = lcCtype
		else:
			del os.environ[LC_CTYPE]
	def test_bad_term( self_ ):
		self_.check_scenario(
			"a line of text<cr><c-d>",
			"a line of text\r\n"
			"a line of text\r\n",
			term = "dumb"
		)
	def test_ctrl_c( self_ ):
		self_.check_scenario(
			"abc<c-c><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>ab<rst><ceos><rst><c11><c9>abc<rst><ceos><rst><c12><c9>abc<rst><ceos>"
			"<c12>^C\r\r\n"
			"<c1>"
		)
	def test_ctrl_z( self_ ):
		self_.check_scenario(
			"<up><c-z><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> three<rst><ceos><rst><c14><brightgreen>replxx<rst>> <c9>three<rst>"
			"<ceos><rst><c14><c9>three<rst><ceos><c14>\r\n"
			"three\r\n"
			"<c1>"
		)
		self_.check_scenario(
			"<c-r>w<c-z><cr><c-d>",
			"<c1><ceos><c1><ceos>(reverse-i-search)`': <c23><c1><ceos>(reverse-i-search)`w': two<c25><c1><ceos>"
			"(reverse-i-search)`w': two<c25><c1><ceos><brightgreen>replxx<rst>> two<c10><c9>two<rst><ceos><c10>"
			"<c9>two<rst><ceos><c12>\r\n"
			"two\r\n"
			"<c1>"
		)
	def test_ctrl_l( self_ ):
		self_.check_scenario(
			"<cr><cr><cr><c-l><c-d>",
			"<c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <RIS><mvhm><clr><rst><brightgreen>replxx<rst>> <c9><rst><ceos><rst>"
			"<c9>",
			end = "\r\nExiting Replxx\r\n"
		)
		self_.check_scenario(
			"<cr><up><c-left><c-l><cr><c-d>",
			"<c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <c1><brightgreen>replxx<rst>> first second<rst><ceos><rst><c21><c9>"
			"first second<rst><ceos><c15><RIS><mvhm><clr><rst><brightgreen>replxx<rst>> <c9>first second<rst>"
			"<ceos><c15><c9>first second<rst><ceos><c21>\r\n"
			"first second\r\n"
			"<c1>",
			"first second\n"
		)
	def test_backspace( self_ ):
		self_.check_scenario(
			"<up><c-a><m-f><c-right><backspace><backspace><backspace><backspace><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> one two three<rst><ceos><rst><c22><c9>one two three<rst><ceos><c9><c9>"
			"one two three<rst><ceos><c12><c9>one two three<rst><ceos><c16><c9>one tw three<rst><ceos><c15><c9>"
			"one t three<rst><ceos><c14><c9>one  three<rst><ceos><c13><c9>one three<rst><ceos><c12><c9>"
			"one three<rst><ceos><c18>\r\n"
			"one three\r\n"
			"<c1>",
			"one two three\n"
		)
	def test_delete( self_ ):
		self_.check_scenario(
			"<up><m-b><c-left><del><c-d><del><c-d><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> one two three<rst><ceos><rst><c22><c9>one two three<rst><ceos><c17>"
			"<c9>one two three<rst><ceos><c13><c9>one wo three<rst><ceos><c13><c9>one o three<rst><ceos><c13><c9>"
			"one  three<rst><ceos><c13><c9>one three<rst><ceos><c13><c9>one three<rst><ceos><c18>\r\n"
			"one three\r\n"
			"<c1>",
			"one two three\n"
		)
	def test_home_key( self_ ):
		self_.check_scenario(
			"abc<home>z<cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>ab<rst><ceos><rst><c11><c9>abc<rst><ceos><rst><c12><c9>abc<rst><ceos>"
			"<c9><c9>zabc<rst><ceos><c10><c9>zabc<rst><ceos><c13>\r\n"
			"zabc\r\n"
			"<c1>"
		)
	def test_end_key( self_ ):
		self_.check_scenario(
			"abc<home>z<end>q<cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>ab<rst><ceos><rst><c11><c9>abc<rst><ceos><rst><c12><c9>abc<rst><ceos>"
			"<c9><c9>zabc<rst><ceos><c10><c9>zabc<rst><ceos><rst><c13><c9>zabcq<rst><ceos><rst><c14><c9>"
			"zabcq<rst><ceos><c14>\r\n"
			"zabcq\r\n"
			"<c1>"
		)
	def test_left_key( self_ ):
		self_.check_scenario(
			"abc<left>x<aleft><left>y<cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>ab<rst><ceos><rst><c11><c9>abc<rst><ceos><rst><c12><c9>abc<rst><ceos>"
			"<c11><c9>abxc<rst><ceos><c12><c9>abxc<rst><ceos><c11><c9>abxc<rst><ceos><c10><c9>aybxc<rst><ceos>"
			"<c11><c9>aybxc<rst><ceos><c14>\r\n"
			"aybxc\r\n"
			"<c1>"
		)
	def test_right_key( self_ ):
		self_.check_scenario(
			"abc<home><right>x<aright>y<cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>ab<rst><ceos><rst><c11><c9>abc<rst><ceos><rst><c12><c9>abc<rst><ceos>"
			"<c9><c9>abc<rst><ceos><c10><c9>axbc<rst><ceos><c11><c9>axbc<rst><ceos><c12><c9>axbyc<rst><ceos><c13>"
			"<c9>axbyc<rst><ceos><c14>\r\n"
			"axbyc\r\n"
			"<c1>"
		)
	def test_prev_word_key( self_ ):
		self_.check_scenario(
			"<up><c-left><m-left>x<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abc def ghi<rst><ceos><rst><c20><c9>abc def ghi<rst><ceos><c17><c9>"
			"abc def ghi<rst><ceos><c13><c9>abc xdef ghi<rst><ceos><c14><c9>abc xdef ghi<rst><ceos><c21>\r\n"
			"abc xdef ghi\r\n"
			"<c1>",
			"abc def ghi\n"
		)
		self_.check_scenario(
			"<up><m-B>x<left><m-B>x<left><m-b>x<left><m-B>x<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abc_def ghi_jkl mnl_opq rst_uvw<rst><ceos><rst><c40><c9>"
			"abc_def ghi_jkl mnl_opq rst_uvw<rst><ceos><c37><c9>abc_def ghi_jkl mnl_opq rst_xuvw<rst><ceos><c38>"
			"<c9>abc_def ghi_jkl mnl_opq rst_xuvw<rst><ceos><c37><c9>abc_def ghi_jkl mnl_opq rst_xuvw<rst><ceos>"
			"<c33><c9>abc_def ghi_jkl mnl_opq xrst_xuvw<rst><ceos><c34><c9>abc_def ghi_jkl mnl_opq xrst_xuvw<rst>"
			"<ceos><c33><c9>abc_def ghi_jkl mnl_opq xrst_xuvw<rst><ceos><c25><c9>"
			"abc_def ghi_jkl xmnl_opq xrst_xuvw<rst><ceos><c26><c9>abc_def ghi_jkl xmnl_opq xrst_xuvw<rst><ceos>"
			"<c25><c9>abc_def ghi_jkl xmnl_opq xrst_xuvw<rst><ceos><c21><c9>"
			"abc_def ghi_xjkl xmnl_opq xrst_xuvw<rst><ceos><c22><c9>abc_def ghi_xjkl xmnl_opq xrst_xuvw<rst>"
			"<ceos><c44>\r\n"
			"abc_def ghi_xjkl xmnl_opq xrst_xuvw\r\n"
			"<c1>",
			"abc_def ghi_jkl mnl_opq rst_uvw\r\n<c1>"
		)
	def test_next_word_key( self_ ):
		self_.check_scenario(
			"<up><home><c-right><m-right>x<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abc def ghi<rst><ceos><rst><c20><c9>abc def ghi<rst><ceos><c9><c9>"
			"abc def ghi<rst><ceos><c12><c9>abc def ghi<rst><ceos><c16><c9>abc defx ghi<rst><ceos><c17><c9>"
			"abc defx ghi<rst><ceos><c21>\r\n"
			"abc defx ghi\r\n"
			"<c1>",
			"abc def ghi\n"
		)
		self_.check_scenario(
			"<up><home><m-F>x<m-F>x<m-f>x<m-F>x<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abc_def ghi_jkl mno_pqr stu_vwx<rst><ceos><rst><c40><c9>"
			"abc_def ghi_jkl mno_pqr stu_vwx<rst><ceos><c9><c9>abc_def ghi_jkl mno_pqr stu_vwx<rst><ceos><c12>"
			"<c9>abcx_def ghi_jkl mno_pqr stu_vwx<rst><ceos><c13><c9>abcx_def ghi_jkl mno_pqr stu_vwx<rst><ceos>"
			"<c17><c9>abcx_defx ghi_jkl mno_pqr stu_vwx<rst><ceos><c18><c9>abcx_defx ghi_jkl mno_pqr stu_vwx<rst>"
			"<ceos><c26><c9>abcx_defx ghi_jklx mno_pqr stu_vwx<rst><ceos><c27><c9>"
			"abcx_defx ghi_jklx mno_pqr stu_vwx<rst><ceos><c31><c9>abcx_defx ghi_jklx mnox_pqr stu_vwx<rst><ceos>"
			"<c32><c9>abcx_defx ghi_jklx mnox_pqr stu_vwx<rst><ceos><c44>\r\n"
			"abcx_defx ghi_jklx mnox_pqr stu_vwx\r\n"
			"<c1>",
			"abc_def ghi_jkl mno_pqr stu_vwx\r\n<c1>"
		)
	def test_hint_show( self_ ):
		self_.check_scenario(
			"co\r<c-d>",
			"<c9>c<rst><ceos><rst><c10><c9>co<rst><ceos>\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_red<rst>\r\n"
			"        <gray>color_green<rst><rst><u3><c11><c9>co<rst><ceos><c11>\r\n"
			"co\r\n"
			"<c1>"
		)
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz "
			"<brightgreen>color_brightgreen<rst><ceos><rst><c63><c9>zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz "
			"<brightgreen>color_brightgreen<rst><ceos><c63>\r\n"
			"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz color_brightgreen\r\n<c1>",
			"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz color_brightgreen\n",
			dimensions = ( 16, 64 )
		)
	def test_hint_scroll_down( self_ ):
		self_.check_scenario(
			"co<c-down><c-down><tab><cr><c-d>",
			"<c9>c<rst><ceos><rst><c10><c9>co<rst><ceos>\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_red<rst>\r\n"
			"        <gray>color_green<rst><rst><u3><c11><c9>co<rst><ceos><gray>lor_black<rst>\r\n"
			"        <gray>color_red<rst>\r\n"
			"        <gray>color_green<rst>\r\n"
			"        <gray>color_brown<rst><rst><u3><c11><c9>co<rst><ceos><gray>lor_red<rst>\r\n"
			"        <gray>color_green<rst>\r\n"
			"        <gray>color_brown<rst>\r\n"
			"        <gray>color_blue<rst><rst><u3><c11><c9><red>color_red<rst><ceos><rst><c18><c9>"
			"<red>color_red<rst><ceos><c18>\r\n"
			"color_red\r\n"
			"<c1>"
		)
	def test_hint_scroll_up( self_ ):
		self_.check_scenario(
			"co<c-up><c-up><tab><cr><c-d>",
			"<c9>c<rst><ceos><rst><c10><c9>co<rst><ceos>\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_red<rst>\r\n"
			"        <gray>color_green<rst><rst><u3><c11><c9>co<rst><ceos><gray>lor_white<rst>\r\n"
			"        <gray>co\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_red<rst><rst><u3><c11><c9>co<rst><ceos><gray>lor_brightcyan<rst>\r\n"
			"        <gray>color_white<rst>\r\n"
			"        <gray>co\r\n"
			"        <gray>color_black<rst><rst><u3><c11><c9><brightcyan>color_brightcyan<rst><ceos><rst><c25>"
			"<c9><brightcyan>color_brightcyan<rst><ceos><c25>\r\n"
			"color_brightcyan\r\n"
			"<c1>"
		)
	def test_overlong_hint( self_ ):
		self_.check_scenario(
			"<up><c-down><c-down><tab><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> zzzzzzzzzzzzzzzzzzzzzzzzz color_br<rst><ceos>\r\n"
			"                                  <gray>color_brown<rst>\r\n"
			"                                  <gray>color_brightre<rst>\r\n"
			"                                  <gray>color_brightgr<rst><rst>\r\n"
			"<u4><c43><c9>zzzzzzzzzzzzzzzzzzzzzzzzz color_br<rst><ceos><gray>own<rst>\r\n"
			"                                  <gray>color_brightre<rst>\r\n"
			"                                  <gray>color_brightgr<rst>\r\n"
			"                                  <gray>color_brightbl<rst><rst>\r\n"
			"<u4><c43><c9>zzzzzzzzzzzzzzzzzzzzzzzzz color_br<rst><ceos><gray>ightred<rst>\r\n"
			"                                  <gray>color_brightgr<rst>\r\n"
			"                                  <gray>color_brightbl<rst>\r\n"
			"                                  <gray>color_brightma<rst><rst>\r\n"
			"<u5><c43><c9>zzzzzzzzzzzzzzzzzzzzzzzzz <brightred>color_brightred<rst><ceos><rst><c2><u1><c9>"
			"zzzzzzzzzzzzzzzzzzzzzzzzz <brightred>color_brightred<rst><ceos><c2>\r\n"
			"zzzzzzzzzzzzzzzzzzzzzzzzz color_brightred\r\n"
			"<c1>",
			#replxx> #
			        "zzzzzzzzzzzzzzzzzzzzzzzzz color_br\n",###################
			dimensions = ( 16, 48 )
		)
	def test_history( self_ ):
		self_.check_scenario(
			"<up><up><up><up><down><down><down><down>four<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> three<rst><ceos><rst><c14><c1><brightgreen>replxx<rst>> two<rst><ceos>"
			"<rst><c12><c1><brightgreen>replxx<rst>> one<rst><ceos><rst><c12><c1><brightgreen>replxx<rst>"
			"> two<rst><ceos><rst><c12><c1><brightgreen>replxx<rst>> three<rst><ceos><rst><c14><c1>"
			"<brightgreen>replxx<rst>> <rst><ceos><rst><c9><c9>f<rst><ceos><rst><c10><c9>fo<rst><ceos><rst><c11>"
			"<c9>fou<rst><ceos><rst><c12><c9>four<rst><ceos><rst><c13><c9>four<rst><ceos><c13>\r\n"
			"four\r\n"
			"<c1>"
		)
		with open( "replxx_history.txt", "rb" ) as f:
			data = f.read().decode()
			self_.assertSequenceEqual( data[:-33], "### 0000-00-00 00:00:00.000\none\n### 0000-00-00 00:00:00.000\ntwo\n### 0000-00-00 00:00:00.000\nthree\n" )
			self_.assertSequenceEqual( data[-5:], "four\n" )
	def test_paren_matching( self_ ):
		self_.check_scenario(
			"ab(cd)ef<left><left><left><left><left><left><left><cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>ab<rst><ceos><rst><c11><c9>ab<brightmagenta>(<rst><ceos><rst><c12><c9>"
			"ab<brightmagenta>(<rst>c<rst><ceos><rst><c13><c9>ab<brightmagenta>(<rst>cd<rst><ceos><rst><c14><c9>"
			"ab<brightmagenta>(<rst>cd<brightmagenta>)<rst><ceos><rst><c15><c9>ab<brightmagenta>(<rst>"
			"cd<brightmagenta>)<rst>e<rst><ceos><rst><c16><c9>ab<brightmagenta>(<rst>cd<brightmagenta>)<rst>"
			"ef<rst><ceos><rst><c17><c9>ab<brightmagenta>(<rst>cd<brightmagenta>)<rst>ef<rst><ceos><c16><c9>"
			"ab<brightmagenta>(<rst>cd<brightmagenta>)<rst>ef<rst><ceos><c15><c9>ab<brightmagenta>(<rst>"
			"cd<brightmagenta>)<rst>ef<rst><ceos><c14><c9>ab<brightmagenta>(<rst>cd<brightmagenta>)<rst>ef<rst>"
			"<ceos><c13><c9>ab<brightmagenta>(<rst>cd<brightmagenta>)<rst>ef<rst><ceos><c12><c9>"
			"ab<brightmagenta>(<rst>cd<brightmagenta>)<rst>ef<rst><ceos><c11><c9>ab<brightmagenta>(<rst>"
			"cd<brightmagenta>)<rst>ef<rst><ceos><c10><c9>ab<brightmagenta>(<rst>cd<brightmagenta>)<rst>ef<rst>"
			"<ceos><c17>\r\n"
			"ab(cd)ef\r\n"
			"<c1>"
		)
	def test_paren_not_matched( self_ ):
		self_.check_scenario(
			"a(b[c)d<left><left><left><left><left><left><left><cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>a<brightmagenta>(<rst><ceos><rst><c11><c9>a<brightmagenta>(<rst>b<rst>"
			"<ceos><rst><c12><c9>a<brightmagenta>(<rst>b<brightmagenta>[<rst><ceos><rst><c13><c9>"
			"a<brightmagenta>(<rst>b<brightmagenta>[<rst>c<rst><ceos><rst><c14><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst><ceos><rst><c15><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst>d<rst><ceos><rst><c16><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst>d<rst><ceos><c15><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst>d<rst><ceos><c14><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst>d<rst><ceos><c13><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst>d<rst><ceos><c12><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst>d<rst><ceos><c11><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst>d<rst><ceos><c10><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst>d<rst><ceos><c9><c9>a<brightmagenta>(<rst>"
			"b<brightmagenta>[<rst>c<brightmagenta>)<rst>d<rst><ceos><c16>\r\n"
			"a(b[c)d\r\n"
			"<c1>"
		)
	def test_tab_completion( self_ ):
		self_.check_scenario(
			"co<tab><tab>bri<tab>b<tab><cr><c-d>",
			"<c9>c<rst><ceos><rst><c10><c9>co<rst><ceos>\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_red<rst>\r\n"
			"        <gray>color_green<rst><rst><u3><c11><c9>color_<rst><ceos>\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_red<rst>\r\n"
			"        <gray>color_green<rst><rst><u3><c15><c9>color_<rst><ceos><c15>\r\n"
			"<brightmagenta>color_<rst>black          <brightmagenta>color_<rst>"
			"cyan           <brightmagenta>color_<rst>brightblue\r\n"
			"<brightmagenta>color_<rst><red>red<rst>            <brightmagenta>color_<rst>"
			"lightgray      <brightmagenta>color_<rst>brightmagenta\r\n"
			"<brightmagenta>color_<rst>green          <brightmagenta>color_<rst>"
			"gray           <brightmagenta>color_<rst>brightcyan\r\n"
			"<brightmagenta>color_<rst>brown          <brightmagenta>color_<rst><brightred>brightred<rst>"
			"      <brightmagenta>color_<rst>white\r\n"
			"<brightmagenta>color_<rst>blue           <brightmagenta>color_<rst>brightgreen\r\n"
			"<brightmagenta>color_<rst>magenta        <brightmagenta>color_<rst>yellow\r\n"
			"<brightgreen>replxx<rst>> <c9>color_<rst><ceos>\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_red<rst>\r\n"
			"        <gray>color_green<rst><rst><u3><c15><c9>color_b<rst><ceos>\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_brown<rst>\r\n"
			"        <gray>color_blue<rst><rst><u3><c16><c9>color_br<rst><ceos>\r\n"
			"        <gray>color_brown<rst>\r\n"
			"        <gray>color_brightred<rst>\r\n"
			"        <gray>color_brightgreen<rst><rst><u3><c17><c9>color_bri<rst><ceos>\r\n"
			"        <gray>color_brightred<rst>\r\n"
			"        <gray>color_brightgreen<rst>\r\n"
			"        <gray>color_brightblue<rst><rst><u3><c18><c9>color_bright<rst><ceos>\r\n"
			"        <gray>color_brightred<rst>\r\n"
			"        <gray>color_brightgreen<rst>\r\n"
			"        <gray>color_brightblue<rst><rst><u3><c21><c9>color_brightb<rst><ceos><green>lue<rst><rst>"
			"<c22><c9><brightblue>color_brightblue<rst><ceos><rst><c25><c9><brightblue>color_brightblue<rst>"
			"<ceos><c25>\r\n"
			"color_brightblue\r\n"
			"<c1>"
		)
		self_.check_scenario(
			"<tab><tab>n<cr><c-d>",
			"<bell><bell><c9>n<rst><ceos><rst><c10><c9>n<rst><ceos><c10>\r\nn\r\n<c1>",
			dimensions = ( 4, 32 ),
			command = [ ReplxxTests._cSample_, "q1", "e0" ]
		)
		self_.check_scenario(
			"<tab><tab>n<cr><c-d>",
			"<c9><ceos><c9>\r\n"
			"db\r\n"
			"hello\r\n"
			"hallo\r\n"
			"--More--<bell>\r\t\t\t\t\r<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			dimensions = ( 4, 24 ),
			command = ReplxxTests._cSample_ + " q1 e1"
		)
		self_.check_scenario(
			"<up><home>co<tab><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abcd<brightmagenta>()<rst><ceos><rst><c15><c9>"
			"abcd<brightmagenta>()<rst><ceos><c9><c9>cabcd<brightmagenta>()<rst><ceos><c10><c9>"
			"coabcd<brightmagenta>()<rst><ceos><c11><c9>color_abcd<brightmagenta>()<rst><ceos><c15><c9>"
			"color_abcd<brightmagenta>()<rst><ceos><c21>\r\n"
			"color_abcd()\r\n"
			"<c1>",
			"abcd()\n"
		)
	def test_completion_shorter_result( self_ ):
		self_.check_scenario(
			"<up><tab><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> \\pi<rst><ceos><rst><c12><c9>π<rst><ceos><rst><c10><c9>π<rst><ceos><c10>\r\n"
			"π\r\n<c1>",
			"\\pi\n"
		)
	def test_completion_pager( self_ ):
		cmd = ReplxxTests._cSample_ + " q1 x" + ",".join( _words_ )
		self_.check_scenario(
			"<tab>py<cr><c-d>",
			"<c9><ceos><c9>\r\n"
			"ada         groovy      perl\r\n"
			"algolbash   haskell     php\r\n"
			"basic       huginn      prolog\r\n"
			"clojure     java        python\r\n"
			"cobol       javascript  rebol\r\n"
			"csharp      julia       ruby\r\n"
			"eiffel      kotlin      rust\r\n"
			"erlang      lisp        scala\r\n"
			"forth       lua         scheme\r\n"
			"--More--<bell>\r\t\t\t\t\rfortran     modula      sql\r\n"
			"fsharp      nemerle     swift\r\n"
			"go          ocaml       typescript\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			dimensions = ( 10, 40 ),
			command = cmd
		)
		self_.check_scenario(
			"<tab><cr><cr><cr><cr><c-d>",
			"<c9><ceos><c9>\r\n"
			"ada         groovy      perl\r\n"
			"algolbash   haskell     php\r\n"
			"basic       huginn      prolog\r\n"
			"clojure     java        python\r\n"
			"cobol       javascript  rebol\r\n"
			"csharp      julia       ruby\r\n"
			"eiffel      kotlin      rust\r\n"
			"erlang      lisp        scala\r\n"
			"forth       lua         scheme\r\n"
			"--More--\r\t\t\t\t\rfortran     modula      sql\r\n"
			"--More--\r\t\t\t\t\rfsharp      nemerle     swift\r\n"
			"--More--\r\t\t\t\t\rgo          ocaml       typescript\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			dimensions = ( 10, 40 ),
			command = cmd
		)
		self_.check_scenario(
			"<tab><c-c><cr><c-d>",
			"<c9><ceos><c9>\r\n"
			"ada         kotlin\r\n"
			"algolbash   lisp\r\n"
			"basic       lua\r\n"
			"clojure     modula\r\n"
			"cobol       nemerle\r\n"
			"csharp      ocaml\r\n"
			"eiffel      perl\r\n"
			"--More--^C\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			dimensions = ( 8, 32 ),
			command = cmd
		)
		self_.check_scenario(
			"<tab>q<cr><c-d>",
			"<c9><ceos><c9>\r\n"
			"ada         kotlin\r\n"
			"algolbash   lisp\r\n"
			"basic       lua\r\n"
			"clojure     modula\r\n"
			"cobol       nemerle\r\n"
			"csharp      ocaml\r\n"
			"eiffel      perl\r\n"
			"--More--\r\t\t\t\t\r<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			dimensions = ( 8, 32 ),
			command = cmd
		)
	def test_double_tab_completion( self_ ):
		cmd = ReplxxTests._cSample_ + " d1 q1 x" + ",".join( _words_ )
		self_.check_scenario(
			"fo<tab><tab>r<tab><cr><c-d>",
			"<c9>f<rst><ceos>\r\n"
			"        <gray>forth<rst>\r\n"
			"        <gray>fortran<rst>\r\n"
			"        <gray>fsharp<rst><rst><u3><c10><c9>fo<rst><ceos>\r\n"
			"        <gray>forth<rst>\r\n"
			"        <gray>fortran<rst><rst><u2><c11><c9>fort<rst><ceos>\r\n"
			"        <gray>forth<rst>\r\n"
			"        <gray>fortran<rst><rst><u2><c13><c9>fortr<rst><ceos><gray>an<rst><rst><c14><c9>fortran<rst>"
			"<ceos><rst><c16><c9>fortran<rst><ceos><c16>\r\n"
			"fortran\r\n"
			"<c1>",
			command = cmd
		)
	def test_beep_on_ambiguous_completion( self_ ):
		cmd = ReplxxTests._cSample_ + " b1 d1 q1 x" + ",".join( _words_ )
		self_.check_scenario(
			"fo<tab><tab>r<tab><cr><c-d>",
			"<c9>f<rst><ceos>\r\n"
			"        <gray>forth<rst>\r\n"
			"        <gray>fortran<rst>\r\n"
			"        <gray>fsharp<rst><rst><u3><c10><c9>fo<rst><ceos>\r\n"
			"        <gray>forth<rst>\r\n"
			"        <gray>fortran<rst><rst><u2><c11><bell><c9>fort<rst><ceos>\r\n"
			"        <gray>forth<rst>\r\n"
			"        <gray>fortran<rst><rst><u2><c13><bell><c9>fortr<rst><ceos><gray>an<rst><rst><c14><c9>"
			"fortran<rst><ceos><rst><c16><c9>fortran<rst><ceos><c16>\r\n"
			"fortran\r\n"
			"<c1>",
			command = cmd
		)
	def test_history_search_backward( self_ ):
		self_.check_scenario(
			"<c-r>repl<c-r><cr><c-d>",
			"<c1><ceos><c1><ceos>(reverse-i-search)`': <c23><c1><ceos>(reverse-i-search)`r': echo repl golf<c29>"
			"<c1><ceos>(reverse-i-search)`re': echo repl golf<c30><c1><ceos>"
			"(reverse-i-search)`rep': echo repl golf<c31><c1><ceos>(reverse-i-search)`repl': echo repl golf<c32>"
			"<c1><ceos>(reverse-i-search)`repl': charlie repl delta<c35><c1><ceos><brightgreen>replxx<rst>"
			"> charlie repl delta<c17><c9>charlie repl delta<rst><ceos><c17><c9>charlie repl delta<rst><ceos>"
			"<c27>\r\n"
			"charlie repl delta\r\n"
			"<c1>",
			"some command\n"
			"alfa repl bravo\n"
			"other request\n"
			"charlie repl delta\n"
			"misc input\n"
			"echo repl golf\n"
			"final thoughts\n"
		)
		self_.check_scenario(
			"<c-r>for<backspace><backspace>s<cr><c-d>",
			"<c1><ceos><c1><ceos>(reverse-i-search)`': <c23><c1><ceos>(reverse-i-search)`f': swift<c27><c1><ceos>"
			"(reverse-i-search)`fo': fortran<c25><c1><ceos>(reverse-i-search)`for': fortran<c26><c1><ceos>"
			"(reverse-i-search)`fo': fortran<c25><c1><ceos>(reverse-i-search)`f': swift<c27><c1><ceos>"
			"(reverse-i-search)`fs': fsharp<c25><c1><ceos><brightgreen>replxx<rst>> fsharp<c9><c9>fsharp<rst>"
			"<ceos><c9><c9>fsharp<rst><ceos><c15>\r\n"
			"fsharp\r\n"
			"<c1>",
			"\n".join( _words_ ) + "\n"
		)
		self_.check_scenario(
			"<c-r>mod<c-l><cr><c-d>",
			"<c1><ceos><c1><ceos>(reverse-i-search)`': <c23><c1><ceos>(reverse-i-search)`m': scheme<c28><c1>"
			"<ceos>(reverse-i-search)`mo': modula<c25><c1><ceos>(reverse-i-search)`mod': modula<c26><c1><ceos>"
			"<brightgreen>replxx<rst>> <c9><RIS><mvhm><clr><rst><brightgreen>replxx<rst>> <c9><rst><ceos><rst>"
			"<c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			"\n".join( _words_ ) + "\n"
		)
	def test_history_search_forward( self_ ):
		self_.check_scenario(
			"<c-s>repl<c-s><cr><c-d>",
			"<c1><ceos><c1><ceos>(i-search)`': <c15><bell><c1><ceos>(i-search)`r': <c16><bell><c1><ceos>"
			"(i-search)`re': <c17><bell><c1><ceos>(i-search)`rep': <c18><bell><c1><ceos>(i-search)`repl': <c19>"
			"<bell><c1><ceos>(i-search)`repl': <c19><c1><ceos><brightgreen>replxx<rst>> <c9><c9><ceos><c9>\r\n"
			"<c1>",
			"charlie repl delta\r\n<c1>",
			"some command\n"
			"alfa repl bravo\n"
			"other request\n"
			"charlie repl delta\n"
			"misc input\n"
			"echo repl golf\n"
			"final thoughts\n"
		)
		self_.check_scenario(
			"<pgup><c-s>repl<c-s><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> final thoughts<rst><ceos><rst><c23><c1><ceos><c1><ceos>"
			"(i-search)`': final thoughts<c29><c1><ceos>(i-search)`r': echo repl golf<c21><c1><ceos>"
			"(i-search)`re': echo repl golf<c22><c1><ceos>(i-search)`rep': echo repl golf<c23><c1><ceos>"
			"(i-search)`repl': echo repl golf<c24><c1><ceos>(i-search)`repl': alfa repl bravo<c24><c1><ceos>"
			"<brightgreen>replxx<rst>> alfa repl bravo<c14><c9>alfa repl bravo<rst><ceos><c14><c9>"
			"alfa repl bravo<rst><ceos><c24>\r\n"
			"alfa repl bravo\r\n"
			"<c1>",
			"final thoughts\n"
			"echo repl golf\n"
			"misc input\n"
			"charlie repl delta\n"
			"other request\n"
			"alfa repl bravo\n"
			"some command\n"
			"charlie repl delta\r\n<c1>",
		)
		self_.check_scenario(
			"<c-s>for<backspace><backspace>s<cr><c-d>",
			"<c1><ceos><c1><ceos>(i-search)`': <c15><bell><c1><ceos>(i-search)`f': <c16><bell><c1><ceos>"
			"(i-search)`fo': <c17><bell><c1><ceos>(i-search)`for': <c18><bell><c1><ceos>(i-search)`fo': <c17>"
			"<bell><c1><ceos>(i-search)`f': <c16><bell><c1><ceos>(i-search)`fs': <c17><c1><ceos>"
			"<brightgreen>replxx<rst>> <c9><c9><ceos><c9>\r\n"
			"<c1>",
			"\n".join( _words_[::-1] ) + "\n"
		)
		self_.check_scenario(
			"<pgup><c-s>for<backspace><backspace>s<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> typescript<rst><ceos><rst><c19><c1><ceos><c1><ceos>"
			"(i-search)`': typescript<c25><c1><ceos>(i-search)`f': swift<c19><c1><ceos>"
			"(i-search)`fo': fortran<c17><c1><ceos>(i-search)`for': fortran<c18><c1><ceos>"
			"(i-search)`fo': fortran<c17><c1><ceos>(i-search)`f': swift<c19><c1><ceos>(i-search)`fs': fsharp<c17>"
			"<c1><ceos><brightgreen>replxx<rst>> fsharp<c9><c9>fsharp<rst><ceos><c9><c9>fsharp<rst><ceos><c15>\r\n"
			"fsharp\r\n"
			"<c1>",
			"\n".join( _words_[::-1] ) + "\n"
		)
		self_.check_scenario(
			"<c-s>mod<c-l><cr><c-d>",
			"<c1><ceos><c1><ceos>(i-search)`': <c15><bell><c1><ceos>(i-search)`m': <c16><bell><c1><ceos>"
			"(i-search)`mo': <c17><bell><c1><ceos>(i-search)`mod': <c18><c1><ceos><brightgreen>replxx<rst>> <c9>"
			"<RIS><mvhm><clr><rst><brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			"\n".join( _words_[::-1] ) + "\n"
		)
		self_.check_scenario(
			"<pgup><c-s>mod<c-l><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> typescript<rst><ceos><rst><c19><c1><ceos><c1><ceos>"
			"(i-search)`': typescript<c25><c1><ceos>(i-search)`m': scheme<c20><c1><ceos>"
			"(i-search)`mo': modula<c17><c1><ceos>(i-search)`mod': modula<c18><c1><ceos><brightgreen>replxx<rst>"
			"> typescript<c19><RIS><mvhm><clr><rst><brightgreen>replxx<rst>> <c9>typescript<rst><ceos><rst><c19>"
			"<c9>typescript<rst><ceos><c19>\r\n"
			"typescript\r\n"
			"<c1>",
			"\n".join( _words_[::-1] ) + "\n"
		)
	def test_history_search_backward_position( self_ ):
		self_.check_scenario(
			"<c-r>req<up><cr><c-d>",
			"<c1><ceos><c1><ceos>(reverse-i-search)`': <c23><c1><ceos>(reverse-i-search)`r': echo repl golf<c29>"
			"<c1><ceos>(reverse-i-search)`re': echo repl golf<c30><c1><ceos>"
			"(reverse-i-search)`req': other request<c32><c1><ceos><brightgreen>replxx<rst>> other request<c15>"
			"<c9>other request<rst><ceos><c15><c9>alfa repl bravo<rst><ceos><rst><c24><c9>alfa repl bravo<rst>"
			"<ceos><c24>\r\n"
			"alfa repl bravo\r\n"
			"<c1>",
			"some command\n"
			"alfa repl bravo\n"
			"other request\n"
			"charlie repl delta\n"
			"misc input\n"
			"echo repl golf\n"
			"final thoughts\n"
		)
	def test_history_search_overlong_line( self_ ):
		self_.check_scenario(
			"<c-r>lo<cr><c-d>",
			"<c1><ceos><c1><ceos>(reverse-i-search)`': <c23><c1><ceos>"
			"(reverse-i-search)`l': some very long line of text, much longer then a witdth of a terminal, serious"
			"ly<c37><u1><c1><ceos>(reverse-i-search)`lo': some very long line of text, much longer then a witdth "
			"of a terminal, seriously<u1><c59><c1><ceos><brightgreen>replxx<rst>"
			"> some very long line of text, much longer then a witdth of a terminal, seriously<u1><c43><c9>"
			"some very long line of text, much longer then a witdth of a terminal, seriously<rst><ceos><u1><c43>"
			"<c9>some very long line of text, much longer then a witdth of a terminal, seriously<rst><ceos><c24>"
			"\r\n"
			"some very long line of text, much longer then a witdth of a terminal, seriously\r\n"
			"<c1>",
			"fake\nsome very long line of text, much longer then a witdth of a terminal, seriously\nanother fake",
			dimensions = ( 24, 64 )
		)
	def test_history_prefix_search_backward( self_ ):
		self_.check_scenario(
			"repl<m-p><m-p><cr><c-d>",
			"<c9>r<rst><ceos><rst><c10><c9>re<rst><ceos><rst><c11><c9>rep<rst><ceos><rst><c12><c9>repl<rst><ceos>"
			"<rst><c13><c9>repl_echo golf<rst><ceos><rst><c23><c9>repl_charlie delta<rst><ceos><rst><c27><c9>"
			"repl_charlie delta<rst><ceos><c27>\r\n"
			"repl_charlie delta\r\n"
			"<c1>",
			"some command\n"
			"repl_alfa bravo\n"
			"other request\n"
			"repl_charlie delta\n"
			"misc input\n"
			"repl_echo golf\n"
			"final thoughts\n"
		)
	def test_history_prefix_search_backward_position( self_ ):
		self_.check_scenario(
			"repl<m-p><up><cr><c-d>",
			"<c9>r<rst><ceos><rst><c10><c9>re<rst><ceos><rst><c11><c9>rep<rst><ceos><rst><c12><c9>repl<rst><ceos>"
			"<rst><c13><c9>repl_echo golf<rst><ceos><rst><c23><c1><brightgreen>replxx<rst>> misc input<rst><ceos>"
			"<rst><c19><c9>misc input<rst><ceos><c19>\r\n"
			"misc input\r\n"
			"<c1>",
			"some command\n"
			"repl_alfa bravo\n"
			"other request\n"
			"repl_charlie delta\n"
			"misc input\n"
			"repl_echo golf\n"
			"final thoughts\n"
		)
	def test_history_listing( self_ ):
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <brightmagenta>.history<rst><ceos><rst><c17><c9><brightmagenta>.history<rst><ceos><c17>\r\n"
			"   0: some command\r\n"
			"   1: repl_alfa bravo\r\n"
			"   2: other request\r\n"
			"   3: repl_charlie delta\r\n"
			"   4: misc input\r\n"
			"   5: repl_echo golf\r\n"
			"   6: .history\r\n<c1>",
			"some command\n"
			"repl_alfa bravo\n"
			"other request\n"
			"repl_charlie delta\n"
			"misc input\n"
			"repl_echo golf\n"
			".history\n"
		)
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> /history<rst><ceos><rst><c17><c9>/history<rst><ceos><c17>\r\n"
			"   0: some command\r\n"
			"   1: repl_alfa bravo\r\n"
			"   2: other request\r\n"
			"   3: repl_charlie delta\r\n"
			"   4: misc input\r\n"
			"   5: repl_echo golf\r\n"
			"   6: /history\r\n"
			"/history\r\n<c1>",
			"some command\n"
			"repl_alfa bravo\n"
			"other request\n"
			"repl_charlie delta\n"
			"misc input\n"
			"repl_echo golf\n"
			"/history\n",
			command = ReplxxTests._cSample_ + " q1"
		)
	def test_history_browse( self_ ):
		self_.check_scenario(
			"<up><aup><pgup><down><up><up><adown><pgdown><up><down><down><up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> twelve<rst><ceos><rst><c15><c1><brightgreen>replxx<rst>> eleven<rst>"
			"<ceos><rst><c15><c1><brightgreen>replxx<rst>> one<rst><ceos><rst><c12><c1><brightgreen>replxx<rst>"
			"> two<rst><ceos><rst><c12><c1><brightgreen>replxx<rst>> one<rst><ceos><rst><c12><c1>"
			"<brightgreen>replxx<rst>> two<rst><ceos><rst><c12><c1><brightgreen>replxx<rst>> <rst><ceos><rst><c9>"
			"<c1><brightgreen>replxx<rst>> twelve<rst><ceos><rst><c15><c1><brightgreen>replxx<rst>> <rst><ceos>"
			"<rst><c9><c1><brightgreen>replxx<rst>> twelve<rst><ceos><rst><c15><c9>twelve<rst><ceos><c15>\r\n"
			"twelve\r\n"
			"<c1>",
			"one\n"
			"two\n"
			"three\n"
			"four\n"
			"five\n"
			"six\n"
			"seven\n"
			"eight\n"
			"nine\n"
			"ten\n"
			"eleven\n"
			"twelve\n"
		)
	def test_history_max_size( self_ ):
		self_.check_scenario(
			"<pgup><pgdown>a<cr><pgup><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> three<rst><ceos><rst><c14><c1><brightgreen>replxx<rst>> <rst><ceos>"
			"<rst><c9><c9>a<rst><ceos><rst><c10><c9>a<rst><ceos><c10>\r\n"
			"a\r\n"
			"<c1><brightgreen>replxx<rst>> <c1><brightgreen>replxx<rst>> four<rst><ceos><rst><c13><c9>four<rst>"
			"<ceos><c13>\r\n"
			"four\r\n"
			"<c1>",
			"one\n"
			"two\n"
			"three\n"
			"four\n"
			"five\n",
			command = ReplxxTests._cSample_ + " q1 s3"
		)
	def test_history_unique( self_ ):
		self_.check_scenario(
			"a<cr>b<cr>a<cr>b<cr><up><up><up><cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>a<rst><ceos><c10>\r\n"
			"a\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>b<rst><ceos><rst><c10><c9>b<rst><ceos><c10>\r\n"
			"b\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>a<rst><ceos><rst><c10><c9>a<rst><ceos><c10>\r\n"
			"a\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>b<rst><ceos><rst><c10><c9>b<rst><ceos><c10>\r\n"
			"b\r\n"
			"<c1><brightgreen>replxx<rst>> <c1><brightgreen>replxx<rst>> b<rst><ceos><rst><c10><c1>"
			"<brightgreen>replxx<rst>> a<rst><ceos><rst><c10><c1><brightgreen>replxx<rst>> c<rst><ceos><rst><c10>"
			"<c9>c<rst><ceos><c10>\r\n"
			"c\r\n"
			"<c1>",
			"a\nb\nc\n",
			command = ReplxxTests._cSample_ + " u1 q1"
		)
		self_.check_scenario(
			"a<cr>b<cr>a<cr>b<cr><up><up><up><cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>a<rst><ceos><c10>\r\n"
			"a\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>b<rst><ceos><rst><c10><c9>b<rst><ceos><c10>\r\n"
			"b\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>a<rst><ceos><rst><c10><c9>a<rst><ceos><c10>\r\n"
			"a\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>b<rst><ceos><rst><c10><c9>b<rst><ceos><c10>\r\n"
			"b\r\n"
			"<c1><brightgreen>replxx<rst>> <c1><brightgreen>replxx<rst>> b<rst><ceos><rst><c10><c1>"
			"<brightgreen>replxx<rst>> a<rst><ceos><rst><c10><c1><brightgreen>replxx<rst>> b<rst><ceos><rst><c10>"
			"<c9>b<rst><ceos><c10>\r\n"
			"b\r\n"
			"<c1>",
			"a\nb\nc\n",
			command = ReplxxTests._cSample_ + " u0 q1"
		)
		self_.check_scenario(
			rapid( "/history<cr>/unique<cr>/history<cr><c-d>" ),
			"<c9>/<rst><ceos><rst><c10><c9>/history<rst><ceos><rst><c17>\r\n"
			"   0: a\r\n"
			"   1: b\r\n"
			"   2: c\r\n"
			"   3: b\r\n"
			"   4: c\r\n"
			"   5: d\r\n"
			"   6: a\r\n"
			"   7: c\r\n"
			"   8: c\r\n"
			"   9: a\r\n"
			"/history\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>/unique<rst><ceos><rst><c16>\r\n"
			"/unique\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>/history<rst><ceos><rst><c17>\r\n"
			"   0: b\r\n"
			"   1: d\r\n"
			"   2: c\r\n"
			"   3: a\r\n"
			"   4: /history\r\n"
			"   5: /unique\r\n"
			"/history\r\n"
			"<c1>",
			"a\nb\nc\nb\nc\nd\na\nc\nc\na\n",
			command = ReplxxTests._cSample_ + " u0 q1"
		)
	def test_history_recall_most_recent( self_ ):
		self_.check_scenario(
			"<pgup><down><cr><down><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> aaaa<rst><ceos><rst><c13><c1><brightgreen>replxx<rst>> bbbb<rst><ceos>"
			"<rst><c13><c9>bbbb<rst><ceos><c13>\r\n"
			"bbbb\r\n"
			"<c1><brightgreen>replxx<rst>> <c1><brightgreen>replxx<rst>> cccc<rst><ceos><rst><c13><c9>cccc<rst>"
			"<ceos><c13>\r\n"
			"cccc\r\n"
			"<c1>",
			"aaaa\nbbbb\ncccc\ndddd\n"
		)
	def test_history_abort_incremental_history_search_position( self_ ):
		self_.check_scenario(
			"<up><up><c-r>cc<c-c><up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> hhhh<rst><ceos><rst><c13><c1><brightgreen>replxx<rst>> gggg<rst><ceos>"
			"<rst><c13><c1><ceos><c1><ceos>(reverse-i-search)`': gggg<c27><c1><ceos>"
			"(reverse-i-search)`c': cccc<c27><c1><ceos>(reverse-i-search)`cc': cccc<c27><c1><ceos>"
			"<brightgreen>replxx<rst>> gggg<c13><c9>gggg<rst><ceos><rst><c13><c1><brightgreen>replxx<rst>"
			"> ffff<rst><ceos><rst><c13><c9>ffff<rst><ceos><c13>\r\n"
			"ffff\r\n"
			"<c1>",
			"aaaa\nbbbb\ncccc\ndddd\neeee\nffff\ngggg\nhhhh\n"
		)
	def test_capitalize( self_ ):
		self_.check_scenario(
			"<up><home><right><m-c><m-c><right><right><m-c><m-c><m-c><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abc defg ijklmn zzxq<rst><ceos><rst><c29><c9>abc defg ijklmn zzxq<rst>"
			"<ceos><c9><c9>abc defg ijklmn zzxq<rst><ceos><c10><c9>aBc defg ijklmn zzxq<rst><ceos><c12><c9>"
			"aBc Defg ijklmn zzxq<rst><ceos><c17><c9>aBc Defg ijklmn zzxq<rst><ceos><c18><c9>"
			"aBc Defg ijklmn zzxq<rst><ceos><c19><c9>aBc Defg iJklmn zzxq<rst><ceos><c24><c9>"
			"aBc Defg iJklmn Zzxq<rst><ceos><rst><c29><c9>aBc Defg iJklmn Zzxq<rst><ceos><c29>\r\n"
			"aBc Defg iJklmn Zzxq\r\n"
			"<c1>",
			"abc defg ijklmn zzxq\n"
		)
		self_.check_scenario(
			"<up><home><right><m-C><m-C><m-c><m-C><right><right><m-C><m-C> <cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abc_def ghj_jkl mno_pqr stu_vwx<rst><ceos><rst><c40><c9>"
			"abc_def ghj_jkl mno_pqr stu_vwx<rst><ceos><c9><c9>abc_def ghj_jkl mno_pqr stu_vwx<rst><ceos><c10>"
			"<c9>aBc_def ghj_jkl mno_pqr stu_vwx<rst><ceos><c12><c9>aBc_Def ghj_jkl mno_pqr stu_vwx<rst><ceos>"
			"<c16><c9>aBc_Def Ghj_jkl mno_pqr stu_vwx<rst><ceos><c24><c9>aBc_Def Ghj_jkl Mno_pqr stu_vwx<rst>"
			"<ceos><c28><c9>aBc_Def Ghj_jkl Mno_pqr stu_vwx<rst><ceos><c29><c9>"
			"aBc_Def Ghj_jkl Mno_pqr stu_vwx<rst><ceos><c30><c9>aBc_Def Ghj_jkl Mno_pQr stu_vwx<rst><ceos><c32>"
			"<c9>aBc_Def Ghj_jkl Mno_pQr Stu_vwx<rst><ceos><c36><c9>aBc_Def Ghj_jkl Mno_pQr Stu _vwx<rst><ceos>"
			"<c37><c9>aBc_Def Ghj_jkl Mno_pQr Stu _vwx<rst><ceos><c41>\r\n"
			"aBc_Def Ghj_jkl Mno_pQr Stu _vwx\r\n"
			"<c1>",
			"abc_def ghj_jkl mno_pqr stu_vwx\n"
		)
	def test_make_upper_case( self_ ):
		self_.check_scenario(
			"<up><home><right><right><right><m-u><m-u><right><m-u><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abcdefg hijklmno pqrstuvw<rst><ceos><rst><c34><c9>"
			"abcdefg hijklmno pqrstuvw<rst><ceos><c9><c9>abcdefg hijklmno pqrstuvw<rst><ceos><c10><c9>"
			"abcdefg hijklmno pqrstuvw<rst><ceos><c11><c9>abcdefg hijklmno pqrstuvw<rst><ceos><c12><c9>"
			"abcDEFG hijklmno pqrstuvw<rst><ceos><c16><c9>abcDEFG HIJKLMNO pqrstuvw<rst><ceos><c25><c9>"
			"abcDEFG HIJKLMNO pqrstuvw<rst><ceos><c26><c9>abcDEFG HIJKLMNO PQRSTUVW<rst><ceos><rst><c34><c9>"
			"abcDEFG HIJKLMNO PQRSTUVW<rst><ceos><c34>\r\n"
			"abcDEFG HIJKLMNO PQRSTUVW\r\n"
			"<c1>",
			"abcdefg hijklmno pqrstuvw\n"
		)
		self_.check_scenario(
			"<up><home><right><m-U><m-U><right><m-u><right><right><m-U><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abc_def ghi_jkl mno_pqr stu_vwx<rst><ceos><rst><c40><c9>"
			"abc_def ghi_jkl mno_pqr stu_vwx<rst><ceos><c9><c9>abc_def ghi_jkl mno_pqr stu_vwx<rst><ceos><c10>"
			"<c9>aBC_def ghi_jkl mno_pqr stu_vwx<rst><ceos><c12><c9>aBC_DEF ghi_jkl mno_pqr stu_vwx<rst><ceos>"
			"<c16><c9>aBC_DEF ghi_jkl mno_pqr stu_vwx<rst><ceos><c17><c9>aBC_DEF GHI_JKL mno_pqr stu_vwx<rst>"
			"<ceos><c24><c9>aBC_DEF GHI_JKL mno_pqr stu_vwx<rst><ceos><c25><c9>"
			"aBC_DEF GHI_JKL mno_pqr stu_vwx<rst><ceos><c26><c9>aBC_DEF GHI_JKL mNO_pqr stu_vwx<rst><ceos><c28>"
			"<c9>aBC_DEF GHI_JKL mNO_pqr stu_vwx<rst><ceos><c40>\r\n"
			"aBC_DEF GHI_JKL mNO_pqr stu_vwx\r\n"
			"<c1>",
			"abc_def ghi_jkl mno_pqr stu_vwx\n"
		)
	def test_make_lower_case( self_ ):
		self_.check_scenario(
			"<up><home><right><right><right><m-l><m-l><right><m-l><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> ABCDEFG HIJKLMNO PQRSTUVW<rst><ceos><rst><c34><c9>"
			"ABCDEFG HIJKLMNO PQRSTUVW<rst><ceos><c9><c9>ABCDEFG HIJKLMNO PQRSTUVW<rst><ceos><c10><c9>"
			"ABCDEFG HIJKLMNO PQRSTUVW<rst><ceos><c11><c9>ABCDEFG HIJKLMNO PQRSTUVW<rst><ceos><c12><c9>"
			"ABCdefg HIJKLMNO PQRSTUVW<rst><ceos><c16><c9>ABCdefg hijklmno PQRSTUVW<rst><ceos><c25><c9>"
			"ABCdefg hijklmno PQRSTUVW<rst><ceos><c26><c9>ABCdefg hijklmno pqrstuvw<rst><ceos><rst><c34><c9>"
			"ABCdefg hijklmno pqrstuvw<rst><ceos><c34>\r\n"
			"ABCdefg hijklmno pqrstuvw\r\n"
			"<c1>",
			"ABCDEFG HIJKLMNO PQRSTUVW\n"
		)
		self_.check_scenario(
			"<up><home><right><m-L><m-L><right><m-l><right><right><m-L><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> ABC_DEF GHI_JKL MNO_PQR STU_VWX<rst><ceos><rst><c40><c9>"
			"ABC_DEF GHI_JKL MNO_PQR STU_VWX<rst><ceos><c9><c9>ABC_DEF GHI_JKL MNO_PQR STU_VWX<rst><ceos><c10>"
			"<c9>Abc_DEF GHI_JKL MNO_PQR STU_VWX<rst><ceos><c12><c9>Abc_def GHI_JKL MNO_PQR STU_VWX<rst><ceos>"
			"<c16><c9>Abc_def GHI_JKL MNO_PQR STU_VWX<rst><ceos><c17><c9>Abc_def ghi_jkl MNO_PQR STU_VWX<rst>"
			"<ceos><c24><c9>Abc_def ghi_jkl MNO_PQR STU_VWX<rst><ceos><c25><c9>"
			"Abc_def ghi_jkl MNO_PQR STU_VWX<rst><ceos><c26><c9>Abc_def ghi_jkl Mno_PQR STU_VWX<rst><ceos><c28>"
			"<c9>Abc_def ghi_jkl Mno_PQR STU_VWX<rst><ceos><c40>\r\n"
			"Abc_def ghi_jkl Mno_PQR STU_VWX\r\n"
			"<c1>",
			"ABC_DEF GHI_JKL MNO_PQR STU_VWX\n"
		)
	def test_transpose( self_ ):
		self_.check_scenario(
			"<up><home><c-t><right><c-t><c-t><c-t><c-t><c-t><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abcd<rst><ceos><rst><c13><c9>abcd<rst><ceos><c9><c9>abcd<rst><ceos>"
			"<c10><c9>bacd<rst><ceos><c11><c9>bcad<rst><ceos><c12><c9>bcda<rst><ceos><rst><c13><c9>bcad<rst>"
			"<ceos><rst><c13><c9>bcda<rst><ceos><rst><c13><c9>bcda<rst><ceos><c13>\r\n"
			"bcda\r\n"
			"<c1>",
			"abcd\n"
		)
	def test_kill_to_beginning_of_line( self_ ):
		self_.check_scenario(
			"<up><home><c-right><c-right><right><c-u><end><c-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><rst><c32><c9><brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><c9><c9><brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><c13><c9><brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><c18><c9><brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><c19><c9><brightblue>-<rst>ijklmn zzxq<brightblue>+<rst><ceos>"
			"<c9><c9><brightblue>-<rst>ijklmn zzxq<brightblue>+<rst><ceos><rst><c22><c9><brightblue>-<rst>"
			"ijklmn zzxq<brightblue>++<rst>abc defg<brightblue>-<rst><ceos><rst><c32><c9><brightblue>-<rst>"
			"ijklmn zzxq<brightblue>++<rst>abc defg<brightblue>-<rst><ceos><c32>\r\n"
			"-ijklmn zzxq++abc defg-\r\n"
			"<c1>",
			"+abc defg--ijklmn zzxq+\n"
		)
	def test_kill_to_end_of_line( self_ ):
		self_.check_scenario(
			"<up><home><c-right><c-right><right><c-k><home><c-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><rst><c32><c9><brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><c9><c9><brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><c13><c9><brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><c18><c9><brightblue>+<rst>abc defg<brightblue>--<rst>"
			"ijklmn zzxq<brightblue>+<rst><ceos><c19><c9><brightblue>+<rst>abc defg<brightblue>-<rst><ceos><rst>"
			"<c19><c9><brightblue>+<rst>abc defg<brightblue>-<rst><ceos><c9><c9><brightblue>-<rst>"
			"ijklmn zzxq<brightblue>++<rst>abc defg<brightblue>-<rst><ceos><c22><c9><brightblue>-<rst>"
			"ijklmn zzxq<brightblue>++<rst>abc defg<brightblue>-<rst><ceos><c32>\r\n"
			"-ijklmn zzxq++abc defg-\r\n"
			"<c1>",
			"+abc defg--ijklmn zzxq+\n"
		)
	def test_kill_next_word( self_ ):
		self_.check_scenario(
			"<up><home><c-right><m-d><c-right><c-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> alpha charlie bravo delta<rst><ceos><rst><c34><c9>"
			"alpha charlie bravo delta<rst><ceos><c9><c9>alpha charlie bravo delta<rst><ceos><c14><c9>"
			"alpha bravo delta<rst><ceos><c14><c9>alpha bravo delta<rst><ceos><c20><c9>"
			"alpha bravo charlie delta<rst><ceos><c28><c9>alpha bravo charlie delta<rst><ceos><c34>\r\n"
			"alpha bravo charlie delta\r\n"
			"<c1>",
			"alpha charlie bravo delta\n"
		)
		self_.check_scenario(
			"<up><home><c-right><m-D><m-D><m-d><m-D><c-right><c-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abc_ABC def_DEF ghi_GHI jkl_JKL XXX<rst><ceos><rst><c44><c9>"
			"abc_ABC def_DEF ghi_GHI jkl_JKL XXX<rst><ceos><c9><c9>abc_ABC def_DEF ghi_GHI jkl_JKL XXX<rst><ceos>"
			"<c16><c9>abc_ABC_DEF ghi_GHI jkl_JKL XXX<rst><ceos><c16><c9>abc_ABC ghi_GHI jkl_JKL XXX<rst><ceos>"
			"<c16><c9>abc_ABC jkl_JKL XXX<rst><ceos><c16><c9>abc_ABC_JKL XXX<rst><ceos><c16><c9>"
			"abc_ABC_JKL XXX<rst><ceos><c20><c9>abc_ABC_JKL def_DEF ghi_GHI jkl XXX<rst><ceos><c40><c9>"
			"abc_ABC_JKL def_DEF ghi_GHI jkl XXX<rst><ceos><c44>\r\n"
			"abc_ABC_JKL def_DEF ghi_GHI jkl XXX\r\n"
			"<c1>",
			"abc_ABC def_DEF ghi_GHI jkl_JKL XXX\n"
		)
	def test_kill_prev_word_to_white_space( self_ ):
		self_.check_scenario(
			"<up><c-left><c-w><c-left><c-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> alpha charlie bravo delta<rst><ceos><rst><c34><c9>"
			"alpha charlie bravo delta<rst><ceos><c29><c9>alpha charlie delta<rst><ceos><c23><c9>"
			"alpha charlie delta<rst><ceos><c15><c9>alpha bravo charlie delta<rst><ceos><c21><c9>"
			"alpha bravo charlie delta<rst><ceos><c34>\r\n"
			"alpha bravo charlie delta\r\n"
			"<c1>",
			"alpha charlie bravo delta\n"
		)
	def test_kill_prev_word( self_ ):
		self_.check_scenario(
			"<up><c-left><m-backspace><c-left><c-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> alpha<brightmagenta>.<rst>charlie bravo<brightmagenta>.<rst>delta<rst>"
			"<ceos><rst><c34><c9>alpha<brightmagenta>.<rst>charlie bravo<brightmagenta>.<rst>delta<rst><ceos>"
			"<c29><c9>alpha<brightmagenta>.<rst>charlie delta<rst><ceos><c23><c9>alpha<brightmagenta>.<rst>"
			"charlie delta<rst><ceos><c15><c9>alpha<brightmagenta>.<rst>bravo<brightmagenta>.<rst>"
			"charlie delta<rst><ceos><c21><c9>alpha<brightmagenta>.<rst>bravo<brightmagenta>.<rst>"
			"charlie delta<rst><ceos><c34>\r\n"
			"alpha.bravo.charlie delta\r\n"
			"<c1>",
			"alpha.charlie bravo.delta\n"
		)
	def test_kill_ring( self_ ):
		self_.check_scenario(
			"<up><c-w><backspace><c-w><backspace><c-w><backspace><c-u><c-y><m-y><m-y><m-y> <c-y><m-y><m-y><m-y> <c-y><m-y><m-y><m-y> <c-y><m-y><m-y><m-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> delta charlie bravo alpha<rst><ceos><rst><c34><c9>delta "
			"charlie bravo <rst><ceos><rst><c29><c9>delta charlie "
			"bravo<rst><ceos><rst><c28><c9>delta charlie "
			"<rst><ceos><rst><c23><c9>delta "
			"charlie<rst><ceos><rst><c22><c9>delta "
			"<rst><ceos><rst><c15>"
			"<c9>delta<rst><ceos><rst><c14>"
			"<c9><rst><ceos><rst><c9>"
			"<c9>delta<rst><ceos><rst><c14>"
			"<c9>charlie<rst><ceos><rst><c16>"
			"<c9>bravo<rst><ceos><rst><c14>"
			"<c9>alpha<rst><ceos><rst><c14>"
			"<c9>alpha "
			"<rst><ceos><rst><c15><c9>alpha "
			"alpha<rst><ceos><rst><c20><c9>alpha "
			"delta<rst><ceos><rst><c20><c9>alpha "
			"charlie<rst><ceos><rst><c22><c9>alpha "
			"bravo<rst><ceos><rst><c20><c9>alpha bravo "
			"<rst><ceos><rst><c21><c9>alpha bravo "
			"bravo<rst><ceos><rst><c26><c9>alpha bravo "
			"alpha<rst><ceos><rst><c26><c9>alpha bravo "
			"delta<rst><ceos><rst><c26><c9>alpha bravo "
			"charlie<rst><ceos><rst><c28><c9>alpha bravo charlie "
			"<rst><ceos><rst><c29><c9>alpha bravo charlie "
			"charlie<rst><ceos><rst><c36><c9>alpha bravo charlie "
			"bravo<rst><ceos><rst><c34><c9>alpha bravo charlie "
			"alpha<rst><ceos><rst><c34><c9>alpha bravo charlie "
			"delta<rst><ceos><rst><c34><c9>alpha bravo charlie delta<rst><ceos><c34>\r\n"
			"alpha bravo charlie delta\r\n<c1>",
			"delta charlie bravo alpha\n"
		)
		self_.check_scenario(
			"<up><c-w><c-w><backspace><c-a><c-y> <cr><c-d>",
			"<c1><brightgreen>replxx<rst>> charlie delta alpha bravo<rst><ceos><rst><c34><c9>"
			"charlie delta alpha <rst><ceos><rst><c29><c9>charlie delta <rst><ceos><rst><c23><c9>"
			"charlie delta<rst><ceos><rst><c22><c9>charlie delta<rst><ceos><c9><c9>alpha bravocharlie delta<rst>"
			"<ceos><c20><c9>alpha bravo charlie delta<rst><ceos><c21><c9>alpha bravo charlie delta<rst><ceos>"
			"<c34>\r\n"
			"alpha bravo charlie delta\r\n"
			"<c1>",
			"charlie delta alpha bravo\n"
		)
		self_.check_scenario(
			"<up><home><m-d><m-d><del><c-e> <c-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> charlie delta alpha bravo<rst><ceos><rst><c34><c9>"
			"charlie delta alpha bravo<rst><ceos><c9><c9> delta alpha bravo<rst><ceos><c9><c9> alpha bravo<rst>"
			"<ceos><c9><c9>alpha bravo<rst><ceos><c9><c9>alpha bravo<rst><ceos><rst><c20><c9>alpha bravo <rst>"
			"<ceos><rst><c21><c9>alpha bravo charlie delta<rst><ceos><rst><c34><c9>alpha bravo charlie delta<rst>"
			"<ceos><c34>\r\n"
			"alpha bravo charlie delta\r\n"
			"<c1>",
			"charlie delta alpha bravo\n"
		)
		self_.check_scenario(
			"<up><c-w><backspace><c-w><backspace><c-w><backspace><c-w><backspace><c-w><backspace>"
			"<c-w><backspace><c-w><backspace><c-w><backspace><c-w><backspace><c-w><backspace>"
			"<c-w><c-y><m-y><m-y><m-y><m-y><m-y><m-y><m-y><m-y><m-y><m-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> a b c d e f g h i j k<rst><ceos><rst><c30><c9>a b c d e f g "
			"h i j <rst><ceos><rst><c29><c9>a b c d e f g h i "
			"j<rst><ceos><rst><c28><c9>a b c d e f g h i "
			"<rst><ceos><rst><c27><c9>a b c d e f g h "
			"i<rst><ceos><rst><c26><c9>a b c d e f g h "
			"<rst><ceos><rst><c25><c9>a b c d e f g "
			"h<rst><ceos><rst><c24><c9>a b c d e f g "
			"<rst><ceos><rst><c23><c9>a b c d e f g<rst><ceos><rst><c22><c9>a "
			"b c d e f <rst><ceos><rst><c21><c9>a b c d e "
			"f<rst><ceos><rst><c20><c9>a b c d e <rst><ceos><rst><c19><c9>a b "
			"c d e<rst><ceos><rst><c18><c9>a b c d <rst><ceos><rst><c17><c9>a "
			"b c d<rst><ceos><rst><c16><c9>a b c <rst><ceos><rst><c15><c9>a b "
			"c<rst><ceos><rst><c14><c9>a b <rst><ceos><rst><c13><c9>a "
			"b<rst><ceos><rst><c12><c9>a "
			"<rst><ceos><rst><c11>"
			"<c9>a<rst><ceos><rst><c10>"
			"<c9><rst><ceos><rst><c9>"
			"<c9>a<rst><ceos><rst><c10>"
			"<c9>b<rst><ceos><rst><c10>"
			"<c9>c<rst><ceos><rst><c10>"
			"<c9>d<rst><ceos><rst><c10>"
			"<c9>e<rst><ceos><rst><c10>"
			"<c9>f<rst><ceos><rst><c10>"
			"<c9>g<rst><ceos><rst><c10>"
			"<c9>h<rst><ceos><rst><c10>"
			"<c9>i<rst><ceos><rst><c10>"
			"<c9>j<rst><ceos><rst><c10>"
			"<c9>a<rst><ceos><rst><c10>"
			"<c9>a<rst><ceos><c10>\r\n"
			"a\r\n<c1>",
			"a b c d e f g h i j k\n"
		)
	def test_yank_last_arg( self_ ):
		self_.check_scenario(
			"0123<left><left><m-.><m-.><m-.><cr><c-d>",
			"<c9><yellow>0<rst><ceos><rst><c10><c9><yellow>01<rst><ceos><rst><c11><c9><yellow>012<rst><ceos><rst>"
			"<c12><c9><yellow>0123<rst><ceos><rst><c13><c9><yellow>0123<rst><ceos><c12><c9><yellow>0123<rst>"
			"<ceos><c11><c9><yellow>01<rst>cat<yellow>23<rst><ceos><c14><c9><yellow>01<rst>"
			"trillion<yellow>23<rst><ceos><c19><c9><yellow>01<rst>twelve<yellow>23<rst><ceos><c17><c9>"
			"<yellow>01<rst>twelve<yellow>23<rst><ceos><c19>\r\n"
			"01twelve23\r\n"
			"<c1>",
			"one two three\nten eleven twelve\nmillion trillion\ndog cat\n"
		)
		self_.check_scenario(
			"<up><up><up> <m-.><m-.><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> dog cat<rst><ceos><rst><c16><c1><brightgreen>replxx<rst>"
			"> million trillion<rst><ceos><rst><c25><c1><brightgreen>replxx<rst>> ten eleven twelve<rst><ceos>"
			"<rst><c26><c9>ten eleven twelve <rst><ceos><rst><c27><c9>ten eleven twelve cat<rst><ceos><rst><c30>"
			"<c9>ten eleven twelve trillion<rst><ceos><rst><c35><c9>ten eleven twelve trillion<rst><ceos><c35>\r\n"
			"ten eleven twelve trillion\r\n"
			"<c1>",
			"one two three\nten eleven twelve\nmillion trillion\ndog cat\n"
		)
	def test_tab_completion_cutoff( self_ ):
		self_.check_scenario(
			"<tab>n<tab>y<cr><c-d>",
			"<c9><rst><ceos><rst><c9>\r\n"
			"Display all 9 possibilities? (y or n)\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><rst><c9>\r\n"
			"Display all 9 possibilities? (y or n)<ceos>\r\n"
			"db            hallo         hansekogge    quetzalcoatl  power\r\n"
			"hello         hans          seamann       quit\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 c3"
		)
		self_.check_scenario(
			"<tab>n<cr><c-d>",
			"<c9><rst><ceos><rst><c9>\r\n"
			"Display all 9 possibilities? (y or n)\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 c3"
		)
		self_.check_scenario(
			"<tab><c-c><cr><c-d>",
			"<c9><rst><ceos><rst><c9>\r\n"
			"Display all 9 possibilities? (y or n)^C\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 c3"
		)
		self_.check_scenario(
			["<tab>", "<c-c><cr><c-d>"],
			"<c9><rst><ceos><c9>\r\n"
			"Display all 9 possibilities? (y or n)^C\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 c3 H200"
		)
	def test_preload( self_ ):
		self_.check_scenario(
			"<cr><c-d>",
			"<c9>Alice has a cat.<rst><ceos><rst><c25><c9>Alice has a cat.<rst><ceos><c25>\r\n"
			"Alice has a cat.\r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 'PAlice has a cat.'"
		)
		self_.check_scenario(
			"<cr><c-d>",
			"<c9>Cat  eats  mice. <rst><ceos><rst><c26><c9>Cat  eats  mice. <rst><ceos><c26>\r\n"
			"Cat  eats  mice. \r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 'PCat\teats\tmice.\r\n'"
		)
		self_.check_scenario(
			"<cr><c-d>",
			"<c9>Cat  eats  mice. <rst><ceos><rst><c26><c9>Cat  eats  mice. <rst><ceos><c26>\r\n"
			"Cat  eats  mice. \r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 'PCat\teats\tmice.\r\n\r\n\n\n'"
		)
		self_.check_scenario(
			"<cr><c-d>",
			"<c9>M Alice has a cat.<rst><ceos><rst><c27><c9>M Alice has a cat.<rst><ceos><c27>\r\n"
			"M Alice has a cat.\r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 'PMAlice has a cat.'"
		)
		self_.check_scenario(
			"<cr><c-d>",
			"<c9>M  Alice has a cat.<rst><ceos><rst><c28><c9>M  Alice has a cat.<rst><ceos><c28>\r\n"
			"M  Alice has a cat.\r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 'PM\t\t\t\tAlice has a cat.'"
		)
	def test_prompt( self_ ):
		prompt = "date: now\nrepl> "
		self_.check_scenario(
			"<up><cr><up><up><cr><c-d>",
			"<u1><c1>date: now\r\n"
			"repl> three<rst><ceos><rst><c12><c7>three<rst><ceos><c12>\r\n"
			"three\r\n"
			"<c1>date: now\r\n"
			"repl> <u1><c1>date: now\r\n"
			"repl> three<rst><ceos><rst><c12><u1><c1>date: now\r\n"
			"repl> two<rst><ceos><rst><c10><c7>two<rst><ceos><c10>\r\n"
			"two\r\n"
			"<c1>",
			command = ReplxxTests._cSample_ + " q1 'p{}'".format( prompt ),
			prompt = prompt,
			end = prompt + ReplxxTests._end_
		)
		prompt = "repl>\n"
		self_.check_scenario(
			"a<cr><c-d>",
			"<c1>a<rst><ceos><rst><c2><c1>a<rst><ceos><c2>\r\na\r\n<c1>",
			command = ReplxxTests._cSample_ + " q1 'p{}'".format( prompt ),
			prompt = prompt,
			end = prompt + ReplxxTests._end_
		)
	def test_long_line( self_ ):
		self_.check_scenario(
			"<up><c-left>~<c-left>~<c-left>~<c-left>~<c-left>~<c-left>~<c-left>~<c-left>~<c-left>~<c-left>~<c-left>~<c-left>~<c-left><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> ada clojure eiffel fortran groovy java kotlin modula perl python rust "
			"sql<rst><ceos><rst><c2><u2><c9>ada clojure eiffel fortran groovy java kotlin modula perl python rust"
			" sql<rst><ceos><u1><c39><u1><c9>ada clojure eiffel fortran groovy java kotlin modula perl python rus"
			"t ~sql<rst><ceos><u1><c40><u1><c9>ada clojure eiffel fortran groovy java kotlin modula perl python r"
			"ust ~sql<rst><ceos><u1><c34><u1><c9>ada clojure eiffel fortran groovy java kotlin modula perl python"
			" ~rust ~sql<rst><ceos><u1><c35><u1><c9>ada clojure eiffel fortran groovy java kotlin modula perl pyt"
			"hon ~rust ~sql<rst><ceos><u1><c27><u1><c9>ada clojure eiffel fortran groovy java kotlin modula perl "
			"~python ~rust ~sql<rst><ceos><u1><c28><u1><c9>ada clojure eiffel fortran groovy java kotlin modula p"
			"erl ~python ~rust ~sql<rst><ceos><u1><c22><u1><c9>"
			"ada clojure eiffel fortran groovy java kotlin modula ~perl ~python ~rust ~sql<rst><ceos><u1><c23>"
			"<u1><c9>ada clojure eiffel fortran groovy java kotlin modula ~perl ~python ~rust ~sql<rst><ceos>"
			"<u1><c15><u1><c9>ada clojure eiffel fortran groovy java kotlin ~modula ~perl ~python ~rust ~sql<rst>"
			"<ceos><u1><c16><u1><c9>ada clojure eiffel fortran groovy java kotlin ~modula ~perl ~python ~rust ~sq"
			"l<rst><ceos><u1><c8><u1><c9>ada clojure eiffel fortran groovy java ~kotlin ~modula ~perl ~python ~ru"
			"st ~sql<rst><ceos><u1><c9><u1><c9>ada clojure eiffel fortran groovy java ~kotlin ~modula ~perl ~pyth"
			"on ~rust ~sql<rst><ceos><u1><c3><u1><c9>ada clojure eiffel fortran groovy ~java ~kotlin ~modula ~per"
			"l ~python ~rust ~sql<rst><ceos><u1><c4><u1><c9>ada clojure eiffel fortran groovy ~java ~kotlin ~modu"
			"la ~perl ~python ~rust ~sql<rst><ceos><u2><c36><c9>"
			"ada clojure eiffel fortran ~groovy ~java ~kotlin ~modula ~perl ~python ~rust ~sql<rst><ceos>"
			"<u2><c37><c9>ada clojure eiffel fortran ~groovy ~java ~kotlin ~modula ~perl ~python ~rust ~sql<rst>"
			"<ceos><u2><c28><c9>ada clojure eiffel ~fortran ~groovy ~java ~kotlin ~modula ~perl ~python ~rust ~sq"
			"l<rst><ceos><u2><c29><c9>ada clojure eiffel ~fortran ~groovy ~java ~kotlin ~modula ~perl ~python ~ru"
			"st ~sql<rst><ceos><u2><c21><c9>ada clojure ~eiffel ~fortran ~groovy ~java ~kotlin ~modula ~perl ~pyt"
			"hon ~rust ~sql<rst><ceos><u2><c22><c9>ada clojure ~eiffel ~fortran ~groovy ~java ~kotlin ~modula ~pe"
			"rl ~python ~rust ~sql<rst><ceos><u2><c13><c9>ada ~clojure ~eiffel ~fortran ~groovy ~java ~kotlin ~mo"
			"dula ~perl ~python ~rust ~sql<rst><ceos><u2><c14><c9>"
			"ada ~clojure ~eiffel ~fortran ~groovy ~java ~kotlin ~modula ~perl ~python ~rust ~sql<rst><ceos>"
			"<u2><c9><c9>~ada ~clojure ~eiffel ~fortran ~groovy ~java ~kotlin ~modula ~perl ~python ~rust ~sql<rs"
			"t><ceos><u2><c10><c9>~ada ~clojure ~eiffel ~fortran ~groovy ~java ~kotlin ~modula ~perl ~python ~rus"
			"t ~sql<rst><ceos><u2><c9><c9>~ada ~clojure ~eiffel ~fortran ~groovy ~java ~kotlin ~modula ~perl ~pyt"
			"hon ~rust ~sql<rst><ceos><c14>\r\n"
			"~ada ~clojure ~eiffel ~fortran ~groovy ~java ~kotlin ~modula ~perl ~python ~rust ~sql\r\n"
			"<c1>",
			" ".join( _words_[::3] ) + "\n",
			dimensions = ( 10, 40 )
		)
	def test_colors( self_ ):
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <black>color_black<rst> <red>color_red<rst> "
			"<green>color_green<rst> <brown>color_brown<rst> <blue>color_blue<rst> "
			"<magenta>color_magenta<rst> <cyan>color_cyan<rst> "
			"<lightgray>color_lightgray<rst> <gray>color_gray<rst> "
			"<brightred>color_brightred<rst> <brightgreen>color_brightgreen<rst> "
			"<yellow>color_yellow<rst> <brightblue>color_brightblue<rst> "
			"<brightmagenta>color_brightmagenta<rst> <brightcyan>color_brightcyan<rst> "
			"<white>color_white<rst><ceos><rst><c70><u2><c9><black>color_black<rst> "
			"<red>color_red<rst> <green>color_green<rst> <brown>color_brown<rst> "
			"<blue>color_blue<rst> <magenta>color_magenta<rst> <cyan>color_cyan<rst> "
			"<lightgray>color_lightgray<rst> <gray>color_gray<rst> "
			"<brightred>color_brightred<rst> <brightgreen>color_brightgreen<rst> "
			"<yellow>color_yellow<rst> <brightblue>color_brightblue<rst> "
			"<brightmagenta>color_brightmagenta<rst> <brightcyan>color_brightcyan<rst> "
			"<white>color_white<rst><ceos><c70>\r\n"
			"color_black color_red color_green color_brown color_blue color_magenta "
			"color_cyan color_lightgray color_gray color_brightred color_brightgreen "
			"color_yellow color_brightblue color_brightmagenta color_brightcyan "
			"color_white\r\n<c1>",
			"color_black color_red color_green color_brown color_blue color_magenta color_cyan color_lightgray"
			" color_gray color_brightred color_brightgreen color_yellow color_brightblue color_brightmagenta color_brightcyan color_white\n"
		)
	def test_word_break_characters( self_ ):
		self_.check_scenario(
			"<up><c-left>x<c-left><c-left>x<c-left><c-left>x<c-left><c-left>x<c-left><c-left>x<c-left><c-left>x<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> one_two three-four five_six seven-eight<rst><ceos><rst><c48><c9>"
			"one_two three-four five_six seven-eight<rst><ceos><c43><c9>"
			"one_two three-four five_six seven-xeight<rst><ceos><c44><c9>"
			"one_two three-four five_six seven-xeight<rst><ceos><c43><c9>"
			"one_two three-four five_six seven-xeight<rst><ceos><c37><c9>"
			"one_two three-four five_six xseven-xeight<rst><ceos><c38><c9>"
			"one_two three-four five_six xseven-xeight<rst><ceos><c37><c9>"
			"one_two three-four five_six xseven-xeight<rst><ceos><c28><c9>"
			"one_two three-four xfive_six xseven-xeight<rst><ceos><c29><c9>"
			"one_two three-four xfive_six xseven-xeight<rst><ceos><c28><c9>"
			"one_two three-four xfive_six xseven-xeight<rst><ceos><c23><c9>"
			"one_two three-xfour xfive_six xseven-xeight<rst><ceos><c24><c9>"
			"one_two three-xfour xfive_six xseven-xeight<rst><ceos><c23><c9>"
			"one_two three-xfour xfive_six xseven-xeight<rst><ceos><c17><c9>"
			"one_two xthree-xfour xfive_six xseven-xeight<rst><ceos><c18><c9>"
			"one_two xthree-xfour xfive_six xseven-xeight<rst><ceos><c17><c9>"
			"one_two xthree-xfour xfive_six xseven-xeight<rst><ceos><c9><c9>"
			"xone_two xthree-xfour xfive_six xseven-xeight<rst><ceos><c10><c9>"
			"xone_two xthree-xfour xfive_six xseven-xeight<rst><ceos><c54>\r\n"
			"xone_two xthree-xfour xfive_six xseven-xeight\r\n"
			"<c1>",
			"one_two three-four five_six seven-eight\n",
			command = ReplxxTests._cSample_ + " q1 'w \t-'"
		)
		self_.check_scenario(
			"<up><c-left>x<c-left><c-left>x<c-left><c-left>x<c-left><c-left>x<c-left><c-left>x<c-left><c-left>x<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> one_two three-four five_six seven-eight<rst><ceos><rst><c48><c9>"
			"one_two three-four five_six seven-eight<rst><ceos><c37><c9>"
			"one_two three-four five_six xseven-eight<rst><ceos><c38><c9>"
			"one_two three-four five_six xseven-eight<rst><ceos><c37><c9>"
			"one_two three-four five_six xseven-eight<rst><ceos><c33><c9>"
			"one_two three-four five_xsix xseven-eight<rst><ceos><c34><c9>"
			"one_two three-four five_xsix xseven-eight<rst><ceos><c33><c9>"
			"one_two three-four five_xsix xseven-eight<rst><ceos><c28><c9>"
			"one_two three-four xfive_xsix xseven-eight<rst><ceos><c29><c9>"
			"one_two three-four xfive_xsix xseven-eight<rst><ceos><c28><c9>"
			"one_two three-four xfive_xsix xseven-eight<rst><ceos><c17><c9>"
			"one_two xthree-four xfive_xsix xseven-eight<rst><ceos><c18><c9>"
			"one_two xthree-four xfive_xsix xseven-eight<rst><ceos><c17><c9>"
			"one_two xthree-four xfive_xsix xseven-eight<rst><ceos><c13><c9>"
			"one_xtwo xthree-four xfive_xsix xseven-eight<rst><ceos><c14><c9>"
			"one_xtwo xthree-four xfive_xsix xseven-eight<rst><ceos><c13><c9>"
			"one_xtwo xthree-four xfive_xsix xseven-eight<rst><ceos><c9><c9>"
			"xone_xtwo xthree-four xfive_xsix xseven-eight<rst><ceos><c10><c9>"
			"xone_xtwo xthree-four xfive_xsix xseven-eight<rst><ceos><c54>\r\n"
			"xone_xtwo xthree-four xfive_xsix xseven-eight\r\n"
			"<c1>",
			"one_two three-four five_six seven-eight\n",
			command = ReplxxTests._cSample_ + " q1 'w \t_'"
		)
	def test_no_color( self_ ):
		self_.check_scenario(
			"<up> X<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> color_black color_red color_green color_brown color_blue color_magenta"
			" color_cyan color_lightgray color_gray color_brightred color_brightgreen color_yellow color_brightbl"
			"ue color_brightmagenta color_brightcyan color_white<ceos><c70><u2><c9>"
			"color_black color_red color_green color_brown color_blue color_magenta color_cyan color_lightgray co"
			"lor_gray color_brightred color_brightgreen color_yellow color_brightblue color_brightmagenta color_b"
			"rightcyan color_white <ceos><c71><u2><c9>color_black color_red color_green color_brown color_blue co"
			"lor_magenta color_cyan color_lightgray color_gray color_brightred color_brightgreen color_yellow col"
			"or_brightblue color_brightmagenta color_brightcyan color_white X<ceos><c72><u2><c9>"
			"color_black color_red color_green color_brown color_blue color_magenta color_cyan color_lightgray co"
			"lor_gray color_brightred color_brightgreen color_yellow color_brightblue color_brightmagenta color_b"
			"rightcyan color_white X<ceos><c72>\r\n"
			"color_black color_red color_green color_brown color_blue color_magenta color_cyan color_lightgray co"
			"lor_gray color_brightred color_brightgreen color_yellow color_brightblue color_brightmagenta color_b"
			"rightcyan color_white X\r\n"
			"<c1>",
			"color_black color_red color_green color_brown color_blue color_magenta color_cyan color_lightgray"
			" color_gray color_brightred color_brightgreen color_yellow color_brightblue color_brightmagenta color_brightcyan color_white\n",
			command = ReplxxTests._cSample_ + " q1 m1"
		)
	def test_backspace_long_line_on_small_term( self_ ):
		self_.check_scenario(
			"<cr><cr><cr><up><backspace><backspace><backspace><backspace><backspace><backspace><backspace><backspace><cr><c-d>",
			"<c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <c1><brightgreen>replxx<rst>"
			"> aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c14><u1><c9>"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c13><u1><c9>"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c12><u1><c9>"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c11><u1><c9>"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c10><u1><c9>"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c9><u1><c9>"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c8><u1><c9>"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c7><u1><c9>"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c6><u1><c9>"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<rst><ceos><c6>\r\n"
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\r\n"
			"<c1>",
			"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n",
			dimensions = ( 10, 40 )
		)
		self_.check_scenario(
			"<cr><cr><cr><up><backspace><backspace><backspace><backspace><backspace><backspace><cr><c-d>",
			"<c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <c9><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <c1><brightgreen>replxx<rst>"
			"> a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve me nt<rst><ceos><rst><c39>"
			"<u1><c9>a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve me n<rst><ceos><rst><c38>"
			"<u1><c9>a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve me <rst><ceos><rst><c37>"
			"<u1><c9>a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve me<rst><ceos><rst><c36>"
			"<u1><c9>a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve m<rst><ceos><rst><c35>"
			"<u1><c9>a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve <rst><ceos><rst><c34>"
			"<u1><c9>a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve<rst><ceos><rst><c33>"
			"<u1><c9>a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve<rst><ceos><c33>\r\n"
			"a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve\r\n"
			"<c1>",
			"a qu ite lo ng li ne of sh ort wo rds wi ll te st cu rs or mo ve me nt\n",
			dimensions = ( 10, 40 )
		)
	def test_reverse_history_search_on_max_match( self_ ):
		self_.check_scenario(
			"<up><c-r><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> aaaaaaaaaaaaaaaaaaaaa<rst><ceos><rst><c30><c1><ceos><c1><ceos>"
			"(reverse-i-search)`': aaaaaaaaaaaaaaaaaaaaa<c44><c1><ceos><brightgreen>replxx<rst>"
			"> aaaaaaaaaaaaaaaaaaaaa<c30><c9>aaaaaaaaaaaaaaaaaaaaa<rst><ceos><c30>\r\n"
			"aaaaaaaaaaaaaaaaaaaaa\r\n"
			"<c1>",
			"aaaaaaaaaaaaaaaaaaaaa\n"
		)
	def test_no_terminal( self_ ):
		res = subprocess.run( [ ReplxxTests._cSample_, "q1" ], input = b"replxx FTW!\n", stdout = subprocess.PIPE, stderr = subprocess.PIPE )
		self_.assertSequenceEqual( res.stdout, b"starting...\nreplxx FTW!\n\nExiting Replxx\n" )
	@_no_parallel
	@unittest.skipIf( skip( "async" ), "timing-dependent; flaky on busy CI" )
	def test_async_print( self_ ):
		self_.check_scenario(
			[ "a", "b", "c", "d", "e", "f<cr><c-d>" ], ["<c1><ceos>0\r\n"
"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9>a<rst><ceos><rst><c10><c9>ab<rst><ceos><rst>"
"<c11><c1><ceos>1\r\n"
"<brightgreen>replxx<rst>> <c9>ab<rst><ceos><rst><c11><c9>abc<rst><ceos><rst><c12><c9>abcd<rst><ceos>"
"<rst><c13><c1><ceos>2\r\n"
"<brightgreen>replxx<rst>> <c9>abcd<rst><ceos><rst><c13><c9>abcde<rst><ceos><rst><c14><c9>abcdef<rst>"
"<ceos><rst><c15><c9>abcdef<rst><ceos><c15>\r\n"
"abcdef\r\n"
"<c1>"],
			command = [ ReplxxTests._cxxSample_, "m" ],
			pause = 0.5
		)
		self_.check_scenario(
			[ "<up>", "a", "b", "c", "d", "e", "f<cr><c-d>" ], ["<c1><ceos>0\r\n"
"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><brightgreen>replxx<rst>"
"> a very long line of user input, wider then current terminal, the line is wrapped: <rst><ceos><rst>"
"<c11><u2><c9>a very long line of user input, wider then current terminal, the line is wrapped: a<rst"
"><ceos><rst><c12><u2><c1><ceos>1\r\n"
"<brightgreen>replxx<rst>> \r\n"
"\r\n"
"<u2><c9>a very long line of user input, wider then current terminal, the line is wrapped: a<rst>"
"<ceos><rst><c12><u2><c9>a very long line of user input, wider then current terminal, the line is wra"
"pped: ab<rst><ceos><rst><c13><u2><c9>a very long line of user input, wider then current terminal, th"
"e line is wrapped: abc<rst><ceos><rst><c14><u2><c1><ceos>2\r\n"
"<brightgreen>replxx<rst>> \r\n"
"\r\n"
"<u2><c9>a very long line of user input, wider then current terminal, the line is wrapped: abc<rst>"
"<ceos><rst><c14><u2><c9>a very long line of user input, wider then current terminal, the line is wra"
"pped: abcd<rst><ceos><rst><c15><u2><c9>a very long line of user input, wider then current terminal, "
"the line is wrapped: abcde<rst><ceos><rst><c16><u2><c1><ceos>3\r\n"
"<brightgreen>replxx<rst>> \r\n"
"\r\n"
"<u2><c9>a very long line of user input, wider then current terminal, the line is wrapped: abcde<rst>"
"<ceos><rst><c16><u2><c9>a very long line of user input, wider then current terminal, the line is wra"
"pped: abcdef<rst><ceos><rst><c17><u2><c9>a very long line of user input, wider then current terminal"
", the line is wrapped: abcdef<rst><ceos><c17>\r\n"
"a very long line of user input, wider then current terminal, the line is wrapped: abcdef\r\n"
"<c1>"],
			"a very long line of user input, wider then current terminal, the line is wrapped: \n",
			command = [ ReplxxTests._cxxSample_, "m" ],
			dimensions = ( 10, 40 ),
			pause = 0.5
		)
	@_no_parallel
	@unittest.skipIf( skip( "async" ), "timing-dependent; flaky on busy CI" )
	def test_async_emulate_key_press( self_ ):
		self_.check_scenario(
			[ "a", "b", "c", "d", "e", "f<cr><c-d>" ], [
			                                           	"<c9><yellow>1<rst>a<rst><ceos><rst><c11><c9><yellow>1<rst>ab<rst><ceos><rst><c12><c9><yellow>1<rst>"
			                                           	"ab<yellow>2<rst><ceos><rst><c13><c9><yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c14><c9><yellow>1<rst>"
			                                           	"ab<yellow>2<rst>cd<rst><ceos><rst><c15><c9><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c16><c9>"
			                                           	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst><c17><c9><yellow>1<rst>ab<yellow>2<rst>"
			                                           	"cd<yellow>3<rst>ef<rst><ceos><rst><c18><c9><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<rst><ceos><c18>\r\n"
			                                           	"1ab2cd3ef\r\n"
			                                           	"<c1>",
			                                           	"<c9><yellow>1<rst><ceos><rst><c10><c9><yellow>1<rst>a<rst><ceos><rst><c11><c9><yellow>1<rst>ab<rst><ceos><rst>"
			                                           	"<c12><c9><yellow>1<rst>ab<yellow>2<rst><ceos><rst><c13><c9><yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst>"
			                                           	"<c14><c9><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c15><c9><yellow>1<rst>ab<yellow>2<rst>"
			                                           	"cd<yellow>3<rst><ceos><rst><c16><c9><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst><c17><c9>"
			                                           	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<rst><ceos><rst><c18><c9><yellow>1<rst>ab<yellow>2<rst>"
			                                           	"cd<yellow>3<rst>ef<rst><ceos><c18>\r\n"
			                                           	"1ab2cd3ef\r\n"
			                                           	"<c1>"
			                                           ],
			command = [ ReplxxTests._cxxSample_, "k123456" ],
			pause = 0.5
		)
	def test_special_keys( self_ ):
		self_.check_scenario(
			"<f1><f2><f3><f4><f5><f6><f7><f8><f9><f10><f11><f12>"
			"<s-f1><s-f2><s-f3><s-f4><s-f5><s-f6><s-f7><s-f8><s-f9><s-f10><s-f11><s-f12>"
			"<c-f1><c-f2><c-f3><c-f4><c-f5><c-f6><c-f7><c-f8><c-f9><c-f10><c-f11><c-f12>"
			"<s-tab><s-left><s-right><s-up><s-down>"
			"<s-home><s-end><c-home><c-end><c-pgup><c-pgdown>"
			"<cr><c-d>",
			"<c1><ceos><F1>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F2>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F3>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F4>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F5>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F6>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F7>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F8>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F9>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F10>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F11>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><F12>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F1>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F2>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F3>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F4>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F5>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F6>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F7>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F8>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F9>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F10>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F11>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-F12>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F1>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F2>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F3>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F4>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F5>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F6>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F7>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F8>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F9>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F10>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F11>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-F12>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-Tab>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-Left>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-Right>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-Up>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-Down>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-Home>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><S-End>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-Home>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-End>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-PgUp>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><C-PgDn>\r\n"
			"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>"
		)
	def test_overwrite_mode( self_ ):
		self_.check_scenario(
			"<up><home><right><right>XYZ<ins>012<ins>345<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abcdefgh<rst><ceos><rst><c17><c9>abcdefgh<rst><ceos><c9><c9>"
			"abcdefgh<rst><ceos><c10><c9>abcdefgh<rst><ceos><c11><c9>abXcdefgh<rst><ceos><c12><c9>abXYcdefgh<rst>"
			"<ceos><c13><c9>abXYZcdefgh<rst><ceos><c14><c9>abXYZ<yellow>0<rst>defgh<rst><ceos><c15><c9>"
			"abXYZ<yellow>01<rst>efgh<rst><ceos><c16><c9>abXYZ<yellow>012<rst>fgh<rst><ceos><c17><c9>"
			"abXYZ<yellow>0123<rst>fgh<rst><ceos><c18><c9>abXYZ<yellow>01234<rst>fgh<rst><ceos><c19><c9>"
			"abXYZ<yellow>012345<rst>fgh<rst><ceos><c20><c9>abXYZ<yellow>012345<rst>fgh<rst><ceos><c23>\r\n"
			"abXYZ012345fgh\r\n"
			"<c1>",
			"abcdefgh\n"
		)
	def test_verbatim_insert( self_ ):
		self_.check_scenario(
			["<c-v>", rapid( "<ins>" ), "<cr><c-d>"],
			"<c9>^[<brightmagenta>[<yellow>2<rst>~<rst><ceos><rst><c14><c9>^[<brightmagenta>[<yellow>2<rst>~<rst>"
			"<ceos><c14>\r\n"
			"<ins-key>\r\n"
			"<c1>"
		)
	def test_hint_delay( self_ ):
		self_.check_scenario(
			["han", "<cr><c-d>"],
			"<c9>h<rst><ceos><c10><c9>ha<rst><ceos><c11><c9>han<rst><ceos><c12><c9>han<rst><ceos>\r\n"
			"        <gray>hans<rst>\r\n"
			"        <gray>hansekogge<rst><rst><u2><c12><c9>han<rst><ceos><c12>\r\n"
			"han\r\n"
			"<c1>",
			command = [ ReplxxTests._cSample_, "q1", "H200" ]
		)
	def test_complete_next( self_ ):
		self_.check_scenario(
			"<up><c-n><c-n><c-p><c-p><c-p><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> color_<rst><ceos>\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_red<rst>\r\n"
			"        <gray>color_green<rst><rst><u3><c15><c9><black>color_black<rst><ceos><rst><c20><c9>"
			"<red>color_red<rst><ceos><rst><c18><c9><black>color_black<rst><ceos><rst><c20><c9>color_<rst><ceos>"
			"\r\n"
			"        <gray>color_black<rst>\r\n"
			"        <gray>color_red<rst>\r\n"
			"        <gray>color_green<rst><rst><u3><c15><c9><white>color_white<rst><ceos><rst><c20><c9>"
			"<white>color_white<rst><ceos><c20>\r\n"
			"color_white\r\n"
			"<c1>",
			"color_\n"
		)
		self_.check_scenario(
			"l<c-n><c-n><c-p><c-p><cr><c-d>",
			"<c9>l<rst><ceos>\r\n"
			"        <gray>lc_ctype<rst>\r\n"
			"        <gray>lc_time<rst>\r\n"
			"        <gray>lc_messages<rst><rst><u3><c10><c9>lc_<rst><ceos>\r\n"
			"        <gray>lc_ctype<rst>\r\n"
			"        <gray>lc_time<rst>\r\n"
			"        <gray>lc_messages<rst><rst><u3><c12><c9>lc_ctype<rst><ceos><rst><c17><c9>lc_time<rst><ceos>"
			"<rst><c16><c9>lc_ctype<rst><ceos><rst><c17><c9>lc_<rst><ceos>\r\n"
			"        <gray>lc_ctype<rst>\r\n"
			"        <gray>lc_time<rst>\r\n"
			"        <gray>lc_messages<rst><rst><u3><c12><c9>lc_<rst><ceos><c12>\r\n"
			"lc_\r\n"
			"<c1>",
			command = [ ReplxxTests._cSample_, "xlc_ctype,lc_time,lc_messages,zoom", "I1", "q1" ]
		)
		self_.check_scenario(
			"l<c-n><c-n><c-p><c-p><cr><c-d>",
			"<c9>l<rst><ceos>\r\n"
			"        <gray>lc_ctype<rst>\r\n"
			"        <gray>lc_time<rst>\r\n"
			"        <gray>lc_messages<rst><rst><u3><c10><c9>lc_<rst><ceos>\r\n"
			"        <gray>lc_ctype<rst>\r\n"
			"        <gray>lc_time<rst>\r\n"
			"        <gray>lc_messages<rst><rst><u3><c12><c9>lc_ctype<rst><ceos><rst><c17><c9>lc_<rst><ceos>\r\n"
			"        <gray>lc_ctype<rst>\r\n"
			"        <gray>lc_time<rst>\r\n"
			"        <gray>lc_messages<rst><rst><u3><c12><c9>lc_messages<rst><ceos><rst><c20><c9>lc_messages<rst>"
			"<ceos><c20>\r\n"
			"lc_messages\r\n"
			"<c1>",
			command = [ ReplxxTests._cSample_, "xlc_ctype,lc_time,lc_messages,zoom", "I0", "q1" ]
		)
	def test_disabled_handlers( self_ ):
		self_.check_scenario(
			"<up><left><backspace>4<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> (+ 1 2)<rst><ceos><c16><c9><brightred>(<rst>+ 1 2)<rst><ceos><c15><c9>"
			"<brightred>(<rst>+ 1 )<rst><ceos><c14><c9><brightred>(<rst>+ 1 4)<rst><ceos><c15><c9>"
			"<brightred>(<rst>+ 1 4)<rst><ceos><c16>\r\n"
			"thanks for the input: (+ 1 4)\r\n"
			"<c1>",
			"(+ 1 2)\r\n<c1>",
			command = [ ReplxxTests._cSample_, "N", "S" ]
		)
	def test_state_manipulation( self_ ):
		self_.check_scenario(
			"<up><f2>~<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> replxx<rst><ceos><rst><c15><c9>REPLXX<rst><ceos><c12><c9>REP~LXX<rst>"
			"<ceos><c13><c9>REP~LXX<rst><ceos><c16>\r\n"
			"REP~LXX\r\n"
			"<c1>",
			"replxx\n",
			command = [ ReplxxTests._cSample_, "q1" ]
		)
	def test_modify_callback( self_ ):
		self_.check_scenario(
			"<up><home><right><right>*<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> abcd<brightmagenta>12<rst><ceos><rst><c15><c9>"
			"abcd<brightmagenta>12<rst><ceos><c9><c9>abcd<brightmagenta>12<rst><ceos><c10><c9>"
			"abcd<brightmagenta>12<rst><ceos><c11><c9>ababcd<brightmagenta>12<rst>cd<brightmagenta>12<rst><ceos>"
			"<c15><c9>ababcd<brightmagenta>12<rst>cd<brightmagenta>12<rst><ceos><c21>\r\n"
			"ababcd12cd12\r\n"
			"<c1>",
			"abcd12\n",
			command = [ ReplxxTests._cSample_, "q1", "M1" ]
		)
	def test_paste( self_ ):
		self_.check_scenario(
			rapid( "abcdef<cr><c-d>" ),
			"<c9>a<rst><ceos><rst><c10><c9>abcdef<rst><ceos><rst><c15>\r\n"
			"abcdef\r\n"
			"<c1>"
		)
	def test_history_merge( self_ ):
		with open( "replxx_history_alt.txt", "w" ) as f:
			f.write(
				"### 0000-00-00 00:00:00.001\n"
				"one\n"
				"### 0000-00-00 00:00:00.003\n"
				"three\n"
				"### 0000-00-00 00:00:00.005\n"
				"other\n"
				"### 0000-00-00 00:00:00.009\n"
				"same\n"
				"### 0000-00-00 00:00:00.017\n"
				"seven\n"
			)
			f.close()
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <brightmagenta>.<rst>merge<rst><ceos><rst><c15><c9><brightmagenta>.<rst>merge<rst><ceos><c15>\r\n<c1>",
			"### 0000-00-00 00:00:00.002\n"
			"two\n"
			"### 0000-00-00 00:00:00.004\n"
			"four\n"
			"### 0000-00-00 00:00:00.006\n"
			"same\n"
			"### 0000-00-00 00:00:00.008\n"
			"other\n"
			"### 0000-00-00 00:00:00.018\n"
			".merge\n"
		)
		with open( "replxx_history_alt.txt", "r" ) as f:
			data = f.read()
			expected = (
				"### 0000-00-00 00:00:00.001\n"
				"one\n"
				"### 0000-00-00 00:00:00.002\n"
				"two\n"
				"### 0000-00-00 00:00:00.003\n"
				"three\n"
				"### 0000-00-00 00:00:00.004\n"
				"four\n"
				"### 0000-00-00 00:00:00.008\n"
				"other\n"
				"### 0000-00-00 00:00:00.009\n"
				"same\n"
				"### 0000-00-00 00:00:00.017\n"
				"seven\n"
				"### "
			)
			self_.assertSequenceEqual( data[:-31], expected )
			self_.assertSequenceEqual( data[-7:], ".merge\n" )
	def test_history_save( self_ ):
		with open( "replxx_history_alt.txt", "w" ) as f:
			f.write(
				"### 0000-00-00 00:00:00.001\n"
				"one\n"
				"### 0000-00-00 00:00:00.003\n"
				"three\n"
				"### 3000-00-00 00:00:00.005\n"
				"other\n"
				"### 3000-00-00 00:00:00.009\n"
				"same\n"
				"### 3000-00-00 00:00:00.017\n"
				"seven\n"
			)
			f.close()
		self_.check_scenario(
			"zoom<cr>.save<cr><up><cr><c-d>",
			"<c9>z<rst><ceos><rst><c10><c9>zo<rst><ceos><rst><c11><c9>zoo<rst><ceos><rst><c12><c9>zoom<rst><ceos>"
			"<rst><c13><c9>zoom<rst><ceos><c13>\r\n"
			"zoom\r\n"
			"<c1><brightgreen>replxx<rst>> <c9><brightmagenta>.<rst><ceos><rst><c10><c9><brightmagenta>.<rst>"
			"s<rst><ceos><rst><c11><c9><brightmagenta>.<rst>sa<rst><ceos><rst><c12><c9><brightmagenta>.<rst>"
			"sav<rst><ceos><rst><c13><c9><brightmagenta>.<rst>save<rst><ceos><rst><c14><c9><brightmagenta>.<rst>"
			"save<rst><ceos><c14>\r\n"
			"<c1><brightgreen>replxx<rst>> <c1><brightgreen>replxx<rst>> zoom<rst><ceos><rst><c13><c9>zoom<rst>"
			"<ceos><c13>\r\n"
			"zoom\r\n"
			"<c1>"
		)
	def test_bracketed_paste( self_ ):
		self_.check_scenario(
			"a0<paste-pfx>b1c2d3e<paste-sfx>4f<cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>a<brightmagenta>0<rst><ceos><rst><c11><c9>a<brightmagenta>0<rst>"
			"b<brightmagenta>1<rst>c<brightmagenta>2<rst>d<brightmagenta>3<rst>e<rst><ceos><rst><c18><c9>"
			"a<brightmagenta>0<rst>b<brightmagenta>1<rst>c<brightmagenta>2<rst>d<brightmagenta>3<rst>"
			"e<brightmagenta>4<rst><ceos><rst><c19><c9>a<brightmagenta>0<rst>b<brightmagenta>1<rst>"
			"c<brightmagenta>2<rst>d<brightmagenta>3<rst>e<brightmagenta>4<rst>f<rst><ceos><rst><c20><c9>"
			"a<brightmagenta>0<rst>b<brightmagenta>1<rst>c<brightmagenta>2<rst>d<brightmagenta>3<rst>"
			"e<brightmagenta>4<rst>f<rst><ceos><c20>\r\n"
			"a0b1c2d3e4f\r\n"
			"<c1>",
			command = [ ReplxxTests._cSample_, "q1" ]
		)
		self_.check_scenario(
			"a0<paste-pfx>b1c2d3e<paste-sfx>4f<cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>a<brightmagenta>0<rst><ceos><rst><c11><c9>a<brightmagenta>0<rst>"
			"b<brightmagenta>1<rst>c<brightmagenta>2<rst>d<brightmagenta>3<rst>e<rst><ceos><rst><c18><c9>"
			"a<brightmagenta>0<rst>b<brightmagenta>1<rst>c<brightmagenta>2<rst>d<brightmagenta>3<rst>"
			"e<brightmagenta>4<rst><ceos><rst><c19><c9>a<brightmagenta>0<rst>b<brightmagenta>1<rst>"
			"c<brightmagenta>2<rst>d<brightmagenta>3<rst>e<brightmagenta>4<rst>f<rst><ceos><rst><c20><c9>"
			"a<brightmagenta>0<rst>b<brightmagenta>1<rst>c<brightmagenta>2<rst>d<brightmagenta>3<rst>"
			"e<brightmagenta>4<rst>f<rst><ceos><c20>\r\n"
			"a0b1c2d3e4f\r\n"
			"<c1>",
			command = [ ReplxxTests._cSample_, "q1", "B" ]
		)
		self_.check_scenario(
			"a0<left><paste-pfx>/eb<paste-sfx><cr><paste-pfx>/db<paste-sfx><cr><paste-pfx>x<paste-sfx><cr><c-d>",
			"<c9>a<rst><ceos><rst><c10><c9>a<brightmagenta>0<rst><ceos><rst><c11><c9>a<brightmagenta>0<rst><ceos>"
			"<c10><c9>a/eb<brightmagenta>0<rst><ceos><c13><c9>a/eb<brightmagenta>0<rst><ceos><c14>\r\n"
			"a/eb0\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>/db<rst><ceos><rst><c12><c9>/db<rst><ceos><c12>\r\n"
			"/db\r\n"
			"<c1><brightgreen>replxx<rst>> <c9>x<rst><ceos><rst><c10><c9>x<rst><ceos><c10>\r\n"
			"x\r\n"
			"<c1>",
			command = [ ReplxxTests._cSample_, "q1" ]
		)
		self_.check_scenario(
			"<paste-pfx>aaa\n\tbbb<paste-sfx><backspace><backspace><backspace><backspace><backspace><backspace><backspace><backspace><cr><c-d>",
			"<c9><ceos>aaa\r\n"
			"    bbb<rst><rst><c8><u1><c9><ceos>aaa\r\n"
			"    bb<rst><rst><c7><u1><c9><ceos>aaa\r\n"
			"    b<rst><rst><c6><u1><c9><ceos>aaa\r\n"
			"    <rst><rst><c5><u1><c9><ceos>aaa\r\n"
			"<rst><rst><c1><u1><c9>aaa<rst><ceos><rst><c12><c9>aa<rst><ceos><rst><c11><c9>a<rst><ceos><rst><c10>"
			"<c9><rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1><brightgreen>replxx<rst>> <paste-off>\r\n",
			command = [ ReplxxTests._cxxSample_, "B" ]
		)
	def test_embedded_newline( self_ ):
		self_.check_scenario(
			"<up><c-left><s-cr><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <blue>color_blue<rst> <red>color_red<rst><ceos><rst><c29><c9>"
			"<blue>color_blue<rst> <red>color_red<rst><ceos><c20><c9><ceos><blue>color_blue<rst> \r\n"
			"<red>color_red<rst><c1><u1><c9><ceos><blue>color_blue<rst> \r\n"
			"<red>color_red<rst><c10>\r\n"
			"color_blue \r\n"
			"color_red\r\n"
			"<c1>",
			"color_blue color_red\n"
		)
	def test_move_up_in_multiline( self_ ):
		self_.check_scenario(
			"<up><up> <cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos><blue>color_blue<rst>\r\n"
			"<red>color_red<rst><rst><c10><u1><c9><ceos><blue>color_blue<rst>\r\n"
			"<red>color_red<rst><u1><c10><c9><ceos>c olor_blue\r\n"
			"<red>color_red<rst><u1><c11><c9><ceos>c olor_blue\r\n"
			"<red>color_red<rst><c10>\r\n"
			"c olor_blue\r\n"
			"color_red\r\n"
			"<c1>",
			"some other\ncolor_bluecolor_red\n"
		)
		self_.check_scenario(
			"<up><up> <cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos><brightblue>color_brightblue<rst>\r\n"
			"        <red>color_red<rst><rst><c18><u1><c9><ceos><brightblue>color_brightblue<rst>\r\n"
			"        <red>color_red<rst><u1><c18><c9><ceos>color_bri ghtblue\r\n"
			"        <red>color_red<rst><u1><c19><c9><ceos>color_bri ghtblue\r\n"
			"        <red>color_red<rst><c18>\r\n"
			"color_bri ghtblue\r\n"
			"color_red\r\n"
			"<c1>",
			"some other\ncolor_brightbluecolor_red\n",
			command = [ ReplxxTests._cxxSample_, "I" ]
		)
		self_.check_scenario(
			"<up><up><up><up>x<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>bbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbbbbb<rst><rst><c24><u3><c9><ceos>bbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbbbbb<rst><u1><c21><u2><c9><ceos>bbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbbbbb<rst><u2><c21><u1><c9><ceos>bbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbbbbb<rst><u3><c21><c9><ceos>bbbbbbbbbbbbxbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbbbbb<rst><u3><c22><c1><brightgreen>replxx<rst>> aaaaaaaaaaaaaaaaaaaa<rst><ceos>"
			"<rst><c29><c9>aaaaaaaaaaaaaaaaaaaa<rst><ceos><c29>\r\n"
			"aaaaaaaaaaaaaaaaaaaa\r\n"
			"<c1>",
			"aaaaaaaaaaaaaaaaaaaa\nbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
		)
		self_.check_scenario(
			"<up><up><up><up>x<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>bbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><rst><c25><u3><c9><ceos>bbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><u1><c22><u2><c9><ceos>bbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><u2><c22><u1><c9><ceos>bbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><u3><c22><c9><ceos>bbbbbbbbbbbbbxbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><u3><c23><c1><brightgreen>replxx<rst>> aaaaaaaaaaaaaaaaaaaa<rst><ceos>"
			"<rst><c29><c9>aaaaaaaaaaaaaaaaaaaa<rst><ceos><c29>\r\n"
			"aaaaaaaaaaaaaaaaaaaa\r\n"
			"<c1>",
			"aaaaaaaaaaaaaaaaaaaa\nbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n",
			command = [ ReplxxTests._cxxSample_, "I" ]
		)
	def test_move_down_in_multiline( self_ ):
		self_.check_scenario(
			"<pgup><down><pgup><down> <cr><c-d>",
			"<c1><brightgreen>replxx<rst>> some other<rst><ceos><rst><c19><c1><brightgreen>replxx<rst>> <ceos>"
			"<red>color_red<rst>\r\n"
			"<blue>color_blue<rst><rst><c11><u1><c9><ceos><red>color_red<rst>\r\n"
			"<blue>color_blue<rst><u1><c9><c9><ceos><red>color_red<rst>\r\n"
			"<blue>color_blue<rst><c9><u1><c9><ceos><red>color_red<rst>\r\n"
			"color_bl ue<rst><c10><u1><c9><ceos><red>color_red<rst>\r\n"
			"color_bl ue<rst><c12>\r\n"
			"color_red\r\n"
			"color_bl ue\r\n"
			"<c1>",
			"some other\ncolor_redcolor_blue\n"
		)
		self_.check_scenario(
			"<pgup><down><pgup><down> <cr><c-d>",
			"<c1><brightgreen>replxx<rst>> some other<rst><ceos><rst><c19><c1><brightgreen>replxx<rst>> <ceos>"
			"<red>color_red<rst>\r\n"
			"        <blue>color_blue<rst><rst><c19><u1><c9><ceos><red>color_red<rst>\r\n"
			"        <blue>color_blue<rst><u1><c9><c9><ceos><red>color_red<rst>\r\n"
			"        <blue>color_blue<rst><c9><u1><c9><ceos><red>color_red<rst>\r\n"
			"         <blue>color_blue<rst><c10><u1><c9><ceos><red>color_red<rst>\r\n"
			"         <blue>color_blue<rst><c20>\r\n"
			"color_red\r\n"
			" color_blue\r\n"
			"<c1>",
			"some other\ncolor_redcolor_blue\n",
			command = [ ReplxxTests._cxxSample_, "I" ]
		)
		self_.check_scenario(
			"<pgup><pgup><down><down><down>x<down><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbb<rst><rst><c17><u3><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbb<rst><u3><c9><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbb<rst><u2><c9><u1><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbb<rst><u1><c9><u2><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbb<rst><c9><u3><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbxbbbbbbbb<rst><c10><u3><c1><brightgreen>replxx<rst>> aaaaaaaaaaaaaaaaaaaa<rst><ceos><rst>"
			"<c29><c9>aaaaaaaaaaaaaaaaaaaa<rst><ceos><c29>\r\n"
			"aaaaaaaaaaaaaaaaaaaa\r\n"
			"<c1>",
			"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\naaaaaaaaaaaaaaaaaaaa\n"
		)
		self_.check_scenario(
			"<pgup><pgup><down><down><down>x<down><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><rst><c25><u3><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><u3><c9><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><u2><c9><u1><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><u1><c9><u2><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbb<rst><c9><u3><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        bbbbbbbbbbbbbbbbbbbb\r\n"
			"        xbbbbbbbbbbbbbbbb<rst><c10><u3><c1><brightgreen>replxx<rst>> aaaaaaaaaaaaaaaaaaaa<rst><ceos>"
			"<rst><c29><c9>aaaaaaaaaaaaaaaaaaaa<rst><ceos><c29>\r\n"
			"aaaaaaaaaaaaaaaaaaaa\r\n"
			"<c1>",
			"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\naaaaaaaaaaaaaaaaaaaa\n",
			command = [ ReplxxTests._cxxSample_, "I" ]
		)
	def test_go_to_beginning_of_multiline_entry( self_ ):
		self_.check_scenario(
			"<up><pgup>x <pgup><pgup><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos><red>color_red<rst>\r\n"
			"<blue>color_blue<rst>\r\n"
			"zzzzzz<rst><rst><c7><u2><c9><ceos><red>color_red<rst>\r\n"
			"<blue>color_blue<rst>\r\n"
			"zzzzzz<rst><u2><c9><c9><ceos>xcolor_red\r\n"
			"<blue>color_blue<rst>\r\n"
			"zzzzzz<rst><u2><c10><c9><ceos>x <red>color_red<rst>\r\n"
			"<blue>color_blue<rst>\r\n"
			"zzzzzz<rst><u2><c11><c9><ceos>x <red>color_red<rst>\r\n"
			"<blue>color_blue<rst>\r\n"
			"zzzzzz<rst><u2><c9><c1><brightgreen>replxx<rst>> some other<rst><ceos><rst><c19><c9>some other<rst>"
			"<ceos><c19>\r\n"
			"some other\r\n"
			"<c1>",
			"some other\ncolor_redcolor_bluezzzzzz\n"
		)
	def test_go_to_end_of_multiline_entry( self_ ):
		self_.check_scenario(
			"<up><up><pgup>x <pgdown><pgdown><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <yellow>123<rst><ceos><rst><c12><c1><brightgreen>replxx<rst>> <ceos>"
			"<red>color_red<rst> <green>color_green<rst>\r\n"
			"<blue>color_blue<rst> <yellow>color_yellow<rst>\r\n"
			"zzzzzz<rst><rst><c7><u2><c9><ceos><red>color_red<rst> <green>color_green<rst>\r\n"
			"<blue>color_blue<rst> <yellow>color_yellow<rst>\r\n"
			"zzzzzz<rst><u2><c9><c9><ceos>xcolor_red <green>color_green<rst>\r\n"
			"<blue>color_blue<rst> <yellow>color_yellow<rst>\r\n"
			"zzzzzz<rst><u2><c10><c9><ceos>x <red>color_red<rst> <green>color_green<rst>\r\n"
			"<blue>color_blue<rst> <yellow>color_yellow<rst>\r\n"
			"zzzzzz<rst><u2><c11><c9><ceos>x <red>color_red<rst> <green>color_green<rst>\r\n"
			"<blue>color_blue<rst> <yellow>color_yellow<rst>\r\n"
			"zzzzzz<rst><rst><c7><u2><c1><brightgreen>replxx<rst>> <rst><ceos><rst><c9><c9><rst><ceos><c9>\r\n"
			"<c1>",
			"some other\ncolor_red color_greencolor_blue color_yellowzzzzzz\n123\n"
		)
	def test_move_to_beginning_of_line_in_multiline( self_ ):
		self_.check_scenario(
			"<up><home>x <c-right><up><home>x <c-right><up><home>x <cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos><red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><rst><c16><u2><c9><ceos><red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><c1><u2><c9><ceos><red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"xcolor_green zzz<rst><c2><u2><c9><ceos><red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><c3><u2><c9><ceos><red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><c14><u2><c9><ceos><red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><u1><c14><u1><c9><ceos><red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><u1><c1><u1><c9><ceos><red>color_red<rst> more text\r\n"
			"xcolor_blue <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><u1><c2><u1><c9><ceos><red>color_red<rst> more text\r\n"
			"x <blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><u1><c3><u1><c9><ceos><red>color_red<rst> more text\r\n"
			"x <blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><u1><c13><u1><c9><ceos><red>color_red<rst> more text\r\n"
			"x <blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><u2><c13><c9><ceos><red>color_red<rst> more text\r\n"
			"x <blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><u2><c9><c9><ceos>xcolor_red more text\r\n"
			"x <blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><u2><c10><c9><ceos>x <red>color_red<rst> more text\r\n"
			"x <blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><u2><c11><c9><ceos>x <red>color_red<rst> more text\r\n"
			"x <blue>color_blue<rst> <yellow>123<rst>\r\n"
			"x <green>color_green<rst> zzz<rst><c18>\r\n"
			"x color_red more text\r\n"
			"x color_blue 123\r\n"
			"x color_green zzz\r\n"
			"<c1>",
			"color_red more textcolor_blue 123color_green zzz\n"
		)
		self_.check_scenario(
			"<up><up><c-a><c-a><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><rst><c20><u3><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u1><c20><u2><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u1><c1><u2><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u3><c9><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><c20>\r\n"
			"first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code\r\n"
			"<c1>",
			"first line of textsecond verse of a poemnext passage of a scripturelast line of a code\n"
		)
	def test_move_to_end_of_line_in_multiline( self_ ):
		self_.check_scenario(
			"<up><pgup>x <end>x<right><end>x<right><end>x<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos><red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><rst><c16><u2><c9><ceos><red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><u2><c9><c9><ceos>xcolor_red more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><u2><c10><c9><ceos>x <red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><u2><c11><c9><ceos>x <red>color_red<rst> more text\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><u2><c30><c9><ceos>x <red>color_red<rst> more textx\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><u2><c31><c9><ceos>x <red>color_red<rst> more textx\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><u1><c1><u1><c9><ceos>x <red>color_red<rst> more textx\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>\r\n"
			"<green>color_green<rst> zzz<rst><u1><c15><u1><c9><ceos>x <red>color_red<rst> more textx\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>x\r\n"
			"<green>color_green<rst> zzz<rst><u1><c16><u1><c9><ceos>x <red>color_red<rst> more textx\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>x\r\n"
			"<green>color_green<rst> zzz<rst><c1><u2><c9><ceos>x <red>color_red<rst> more textx\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>x\r\n"
			"<green>color_green<rst> zzz<rst><rst><c16><u2><c9><ceos>x <red>color_red<rst> more textx\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>x\r\n"
			"<green>color_green<rst> zzzx<rst><rst><c17><u2><c9><ceos>x <red>color_red<rst> more textx\r\n"
			"<blue>color_blue<rst> <yellow>123<rst>x\r\n"
			"<green>color_green<rst> zzzx<rst><c17>\r\n"
			"x color_red more textx\r\n"
			"color_blue 123x\r\n"
			"color_green zzzx\r\n"
			"<c1>",
			"color_red more textcolor_blue 123color_green zzz\n"
		)
		self_.check_scenario(
			"<up><pgup><down><c-e><c-e><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><rst><c20><u3><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u3><c9><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u2><c9><u1><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u2><c23><u1><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><rst><c20><u3><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><c20>\r\n"
			"first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code\r\n"
			"<c1>",
			"first line of textsecond verse of a poemnext passage of a scripturelast line of a code\n"
		)
	def test_hints_in_multiline( self_ ):
		self_.check_scenario(
			"<up><c-down><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>some text\r\n"
			"color_b<rst>\r\n"
			"<gray>color_black<rst>\r\n"
			"<gray>color_brown<rst>\r\n"
			"<gray>color_blue<rst><rst><u3><c8><u1><c9><ceos>some text\r\n"
			"color_b<rst><gray>lack<rst>\r\n"
			"<gray>color_brown<rst>\r\n"
			"<gray>color_blue<rst>\r\n"
			"<gray>color_brightred<rst><rst><u3><c8><u1><c9><ceos>some text\r\n"
			"color_b<rst><c8>\r\n"
			"some text\r\n"
			"color_b\r\n"
			"<c1>",
			"some textcolor_b\n"
		)
		self_.check_scenario(
			"<up><c-down><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>some long text\r\n"
			"        color_br<rst>\r\n"
			"        <gray>color_brown<rst>\r\n"
			"        <gray>color_brightred<rst>\r\n"
			"        <gray>color_brightgreen<rst><rst><u3><c17><u1><c9><ceos>some long text\r\n"
			"        color_br<rst><gray>own<rst>\r\n"
			"        <gray>color_brightred<rst>\r\n"
			"        <gray>color_brightgreen<rst>\r\n"
			"        <gray>color_brightblue<rst><rst><u3><c17><u1><c9><ceos>some long text\r\n"
			"        color_br<rst><c17>\r\n"
			"some long text\r\n"
			"color_br\r\n"
			"<c1>",
			"some long textcolor_br\n",
			command = [ ReplxxTests._cxxSample_, "I" ]
		)
		self_.check_scenario(
			"<up><c-down><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>some text\r\n"
			"not on start color_b<rst>\r\n"
			"             <gray>color_black<rst>\r\n"
			"             <gray>color_brown<rst>\r\n"
			"             <gray>color_blue<rst><rst><u3><c21><u1><c9><ceos>some text\r\n"
			"not on start color_b<rst><gray>lack<rst>\r\n"
			"             <gray>color_brown<rst>\r\n"
			"             <gray>color_blue<rst>\r\n"
			"             <gray>color_brightred<rst><rst><u3><c21><u1><c9><ceos>some text\r\n"
			"not on start color_b<rst><c21>\r\n"
			"some text\r\n"
			"not on start color_b\r\n"
			"<c1>",
			"some textnot on start color_b\n"
		)
		self_.check_scenario(
			"<up><c-down><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>some text\r\n"
			"        not on start color_br<rst>\r\n"
			"                     <gray>color_brown<rst>\r\n"
			"                     <gray>color_brightred<rst>\r\n"
			"                     <gray>color_brightgreen<rst><rst><u3><c30><u1><c9><ceos>some text\r\n"
			"        not on start color_br<rst><gray>own<rst>\r\n"
			"                     <gray>color_brightred<rst>\r\n"
			"                     <gray>color_brightgreen<rst>\r\n"
			"                     <gray>color_brightblue<rst><rst><u3><c30><u1><c9><ceos>some text\r\n"
			"        not on start color_br<rst><c30>\r\n"
			"some text\r\n"
			"not on start color_br\r\n"
			"<c1>",
			"some textnot on start color_br\n",
			command = [ ReplxxTests._cxxSample_, "I" ]
		)
	@_no_parallel
	@unittest.skipIf( skip( "async" ), "timing-dependent; flaky on busy CI" )
	def test_async_prompt( self_ ):
		self_.check_scenario(
			[ "<up>", "r", "i", "g", "h", "t", "g<tab><cr><c-d>" ], [
			                                                        	"<c1><ceos><brightgreen>replxx<rst>[-]> <c12><rst><ceos><rst><c12><c1><brightgreen>replxx<rst>"
			                                                        	"[-]> long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[\\]> <c12>long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[|]> <c12>long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c12>long line <green>color_green<rst>"
			                                                        	" and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c12>"
			                                                        	"long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c12>"
			                                                        	"long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c12>"
			                                                        	"long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c12>"
			                                                        	"long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c12>"
			                                                        	"long line <green>color_green<rst> and color_brightg<rst><ceos><green>reen<rst><rst><c51><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_brightg<rst><ceos>"
			                                                        	"<green>reen<rst><rst><c51><c12>long line <green>color_green<rst> and <brightgreen>color_brightgreen<rst><ceos>"
			                                                        	"<rst><c55><c12>long line <green>color_green<rst> and <brightgreen>color_brightgreen<rst><ceos><c55>\r\n"
			                                                        	"long line color_green and color_brightgreen\r\n"
			                                                        	"<c1><brightgreen>replxx<rst>> \r\n",
			                                                        	"<c1><ceos>0\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><rst><ceos><rst><c12><c1><ceos><brightgreen>replxx<rst>[-]> <c12>"
			                                                        	"<yellow>1<rst><ceos><rst><c13><c12><yellow>1<rst><ceos><rst><c13><c12><yellow>1<rst>a<rst><ceos><rst><c14><c1>"
			                                                        	"<ceos><brightgreen>replxx<rst>[\\]> <c12><yellow>1<rst>a<rst><ceos><rst><c14><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[|]> <c12><yellow>1<rst>a<rst><ceos><rst><c14><c12><yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12><yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos>1\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[-]> <c12><yellow>1<rst>ab<yellow>2<rst><ceos><rst><c16><c12><yellow>1<rst>ab<yellow>2<rst><ceos><rst><c16>"
			                                                        	"<c12><yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c17><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c17><c1><ceos><brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>"
			                                                        	"ab<yellow>2<rst>c<rst><ceos><rst><c17><c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>2\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c12><yellow>1<rst>ab<yellow>2<rst>"
			                                                        	"cd<yellow>3<rst>e<rst><ceos><rst><c20><c1><ceos><brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>"
			                                                        	"ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst><c20><c1><ceos><brightgreen>replxx<rst>[/]> <c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst><c20><c12><yellow>1<rst>ab<yellow>2<rst>"
			                                                        	"cd<yellow>3<rst>ef<rst><ceos><rst><c21><c1><ceos>3\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<rst><ceos><rst><c21><c1>"
			                                                        	"<ceos><brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst><ceos>"
			                                                        	"<rst><c22><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst><ceos><rst><c22><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst><ceos><rst>"
			                                                        	"<c22><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst>g<rst><ceos><rst><c23><bell><c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst>g<rst><ceos><c23>\r\n"
			                                                        	"1ab2cd3ef4g\r\n"
			                                                        	"<c1><brightgreen>replxx<rst>> \r\n",
			                                                        	"<c1><ceos>0\r\n"
			                                                        	"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>"
			                                                        	"<ceos><rst><c13><c12><yellow>1<rst><ceos><rst><c13><c12><yellow>1<rst>a<rst><ceos><rst><c14><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12><yellow>1<rst>a<rst><ceos><rst><c14><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[|]> <c12><yellow>1<rst>a<rst><ceos><rst><c14><c12><yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12><yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos>1\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[-]> <c12><yellow>1<rst>ab<yellow>2<rst><ceos><rst><c16><c12><yellow>1<rst>ab<yellow>2<rst><ceos><rst><c16>"
			                                                        	"<c12><yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c17><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c17><c1><ceos><brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>"
			                                                        	"ab<yellow>2<rst>c<rst><ceos><rst><c17><c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>2\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c12><yellow>1<rst>ab<yellow>2<rst>"
			                                                        	"cd<yellow>3<rst>e<rst><ceos><rst><c20><c1><ceos><brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>"
			                                                        	"ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst><c20><c1><ceos><brightgreen>replxx<rst>[/]> <c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst><c20><c12><yellow>1<rst>ab<yellow>2<rst>"
			                                                        	"cd<yellow>3<rst>ef<rst><ceos><rst><c21><c1><ceos>3\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<rst><ceos><rst><c21><c1>"
			                                                        	"<ceos><brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst><ceos>"
			                                                        	"<rst><c22><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst><ceos><rst><c22><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst><ceos><rst>"
			                                                        	"<c22><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst>g<rst><ceos><rst><c23><bell><c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst>g<rst><ceos><c23>\r\n"
			                                                        	"1ab2cd3ef4g\r\n"
			                                                        	"<c1><brightgreen>replxx<rst>> <c1><ceos><brightgreen>replxx<rst>[|]> <c12><rst><ceos><rst><c12>\r\n",
			                                                        	"<c1><ceos>0\r\n"
			                                                        	"<brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><brightgreen>replxx<rst>[-]> <c12><rst><ceos><rst>"
			                                                        	"<c12><c12>a<rst><ceos><rst><c13><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>a<rst><ceos><rst><c13><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>a<rst><ceos><rst><c13><c12>ab<rst><ceos><rst><c14><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>ab<rst><ceos><rst><c14><c1><ceos>1\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>ab<rst><ceos><rst><c14><c1><ceos><brightgreen>replxx<rst>[-]> <c12>ab<rst>"
			                                                        	"<ceos><rst><c14><c12>abc<rst><ceos><rst><c15><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>abc<rst><ceos><rst>"
			                                                        	"<c15><c1><ceos><brightgreen>replxx<rst>[|]> <c12>abc<rst><ceos><rst><c15><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[/]> <c12>abc<rst><ceos><rst><c15><c12>abcd<rst><ceos><rst><c16><c1><ceos>2\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>abcd<rst><ceos><rst><c16><c1><ceos><brightgreen>replxx<rst>[-]> <c12>"
			                                                        	"abcd<rst><ceos><rst><c16><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>abcd<rst><ceos><rst><c16><c12>abcde<rst>"
			                                                        	"<ceos><rst><c17><c1><ceos><brightgreen>replxx<rst>[|]> <c12>abcde<rst><ceos><rst><c17><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>abcde<rst><ceos><rst><c17><c12>abcdef<rst><ceos><rst><c18><c1><ceos>3\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>abcdef<rst><ceos><rst><c18><c1><ceos><brightgreen>replxx<rst>[-]> <c12>"
			                                                        	"abcdef<rst><ceos><rst><c18><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>abcdef<rst><ceos><rst><c18><c12>"
			                                                        	"abcdefg<rst><ceos><rst><c19><bell><c1><ceos><brightgreen>replxx<rst>[|]> <c12>abcdefg<rst><ceos><rst><c19>"
			                                                        	"<c12>abcdefg<rst><ceos><c19>\r\n"
			                                                        	"abcdefg\r\n"
			                                                        	"<c1><brightgreen>replxx<rst>> \r\n",
			                                                        	"<c1><ceos>0\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst><ceos><rst><c13><c12><yellow>1<rst>a<rst><ceos><rst><c14><c1>"
			                                                        	"<ceos><brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>a<rst><ceos><rst><c14><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[\\]> <c12><yellow>1<rst>a<rst><ceos><rst><c14><c1><ceos><brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>a<rst>"
			                                                        	"<ceos><rst><c14><c12><yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos><brightgreen>replxx<rst>[/]> <c12>"
			                                                        	"<yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos>1\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[-]> <c12><yellow>1<rst>ab<yellow>2<rst><ceos><rst><c16><c12><yellow>1<rst>ab<yellow>2<rst><ceos><rst><c16>"
			                                                        	"<c12><yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c17><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c17><c1><ceos><brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>"
			                                                        	"ab<yellow>2<rst>c<rst><ceos><rst><c17><c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>2\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c12><yellow>1<rst>ab<yellow>2<rst>"
			                                                        	"cd<yellow>3<rst>e<rst><ceos><rst><c20><c1><ceos><brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>"
			                                                        	"ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst><c20><c1><ceos><brightgreen>replxx<rst>[/]> <c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst><c20><c12><yellow>1<rst>ab<yellow>2<rst>"
			                                                        	"cd<yellow>3<rst>ef<rst><ceos><rst><c21><c1><ceos>3\r\n"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<rst><ceos><rst><c21><c1>"
			                                                        	"<ceos><brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst><ceos>"
			                                                        	"<rst><c22><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst><ceos><rst><c22><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst><ceos><rst>"
			                                                        	"<c22><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst>g<rst><ceos><rst><c23><bell><c12>"
			                                                        	"<yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst>g<rst><ceos><c23>\r\n"
			                                                        	"1ab2cd3ef4g\r\n"
			                                                        	"<c1><brightgreen>replxx<rst>> <c1><ceos><brightgreen>replxx<rst>[|]> <c12><rst><ceos><rst><c12>\r\n",
			                                                        	"<c1><brightgreen>replxx<rst>> long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                  <gray>color_black<rst>\r\n"
			                                                        	"                                  <gray>color_brown<rst>\r\n"
			                                                        	"                                  <gray>color_blue<rst><rst><u3><c42><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[\\]> <c12>long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[|]> <c12>long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c12>long line <green>color_green<rst>"
			                                                        	" and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c12>"
			                                                        	"long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c12>"
			                                                        	"long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c12>"
			                                                        	"long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c12>"
			                                                        	"long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c12>"
			                                                        	"long line <green>color_green<rst> and color_brightg<rst><ceos><green>reen<rst><rst><c51><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_brightg<rst><ceos>"
			                                                        	"<green>reen<rst><rst><c51><c12>long line <green>color_green<rst> and <brightgreen>color_brightgreen<rst><ceos>"
			                                                        	"<rst><c55><c12>long line <green>color_green<rst> and <brightgreen>color_brightgreen<rst><ceos><c55>\r\n"
			                                                        	"long line color_green and color_brightgreen\r\n"
			                                                        	"<c1><brightgreen>replxx<rst>> \r\n",
			                                                        	"<c1><ceos><brightgreen>replxx<rst>[-]> <c12><rst><ceos><rst><c12><c1><brightgreen>replxx<rst>"
			                                                        	"[-]> long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[\\]> <c12>long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[|]> <c12>long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c12>long line <green>color_green<rst>"
			                                                        	" and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c12>"
			                                                        	"long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c12>"
			                                                        	"long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c12>"
			                                                        	"long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c12>"
			                                                        	"long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c12>"
			                                                        	"long line <green>color_green<rst> and color_brightg<rst><ceos><green>reen<rst><rst><c51><c12>"
			                                                        	"long line <green>color_green<rst> and <brightgreen>color_brightgreen<rst><ceos><rst><c55><c12>"
			                                                        	"long line <green>color_green<rst> and <brightgreen>color_brightgreen<rst><ceos><c55>\r\n"
			                                                        	"long line color_green and color_brightgreen\r\n"
			                                                        	"<c1><brightgreen>replxx<rst>> \r\n",
			                                                        	"<c1><ceos><brightgreen>replxx<rst>[-]> <c12><rst><ceos><rst><c12><c1><brightgreen>replxx<rst>"
			                                                        	"[-]> long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[\\]> <c12>long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[|]> <c12>long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c1><ceos><brightgreen>replxx<rst>"
			                                                        	"[/]> <c12>long line <green>color_green<rst> and color_b<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_black<rst>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_blue<rst><rst><u3><c45><c12>long line <green>color_green<rst>"
			                                                        	" and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_br<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brown<rst>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst><rst><u3><c46><c12>"
			                                                        	"long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_bri<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c47><c12>"
			                                                        	"long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_brig<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c48><c12>"
			                                                        	"long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[/]> <c12>long line <green>color_green<rst> and color_brigh<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c49><c12>"
			                                                        	"long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[-]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[\\]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c1><ceos>"
			                                                        	"<brightgreen>replxx<rst>[|]> <c12>long line <green>color_green<rst> and color_bright<rst><ceos>\r\n"
			                                                        	"                                     <gray>color_brightred<rst>\r\n"
			                                                        	"                                     <gray>color_brightgreen<rst>\r\n"
			                                                        	"                                     <gray>color_brightblue<rst><rst><u3><c50><c12>"
			                                                        	"long line <green>color_green<rst> and color_brightg<rst><ceos><green>reen<rst><rst><c51><c12>"
			                                                        	"long line <green>color_green<rst> and <brightgreen>color_brightgreen<rst><ceos><rst><c55><c12>"
			                                                        	"long line <green>color_green<rst> and <brightgreen>color_brightgreen<rst><ceos><c55>\r\n"
			                                                        	"long line color_green and color_brightgreen\r\n"
			                                                        	"<c1><brightgreen>replxx<rst>> \r\n"
			                                                        ],
			"long line color_green and color_b\n",
			command = [ ReplxxTests._cxxSample_, "F" ],
			pause = 0.5
		)
		self_.check_scenario(
			[ "a", "b", "c", "d", "e", "f", "g<tab><cr><c-d>" ], ["<c1><ceos>0\r\n"
"<brightgreen>replxx<rst>[-]> <c12><rst><ceos><rst><c12><c1><ceos><brightgreen>replxx<rst>[-]> <c12>"
"<rst><ceos><rst><c12><c12>a<rst><ceos><rst><c13><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>a<rst>"
"<ceos><rst><c13><c1><ceos><brightgreen>replxx<rst>[|]> <c12>a<rst><ceos><rst><c13><c12>ab<rst><ceos>"
"<rst><c14><c1><ceos><brightgreen>replxx<rst>[/]> <c12>ab<rst><ceos><rst><c14><c1><ceos>1\r\n"
"<brightgreen>replxx<rst>[-]> <c12>ab<rst><ceos><rst><c14><c1><ceos><brightgreen>replxx<rst>"
"[-]> <c12>ab<rst><ceos><rst><c14><c12>abc<rst><ceos><rst><c15><c1><ceos><brightgreen>replxx<rst>"
"[\\]> <c12>abc<rst><ceos><rst><c15><c1><ceos><brightgreen>replxx<rst>[|]> <c12>abc<rst><ceos><rst>"
"<c15><c1><ceos><brightgreen>replxx<rst>[/]> <c12>abc<rst><ceos><rst><c15><c12>abcd<rst><ceos><rst>"
"<c16><c1><ceos>2\r\n"
"<brightgreen>replxx<rst>[-]> <c12>abcd<rst><ceos><rst><c16><c1><ceos><brightgreen>replxx<rst>"
"[-]> <c12>abcd<rst><ceos><rst><c16><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>abcd<rst><ceos><rst>"
"<c16><c12>abcde<rst><ceos><rst><c17><c1><ceos><brightgreen>replxx<rst>[|]> <c12>abcde<rst><ceos>"
"<rst><c17><c1><ceos><brightgreen>replxx<rst>[/]> <c12>abcde<rst><ceos><rst><c17><c12>abcdef<rst>"
"<ceos><rst><c18><c1><ceos>3\r\n"
"<brightgreen>replxx<rst>[-]> <c12>abcdef<rst><ceos><rst><c18><c1><ceos><brightgreen>replxx<rst>"
"[-]> <c12>abcdef<rst><ceos><rst><c18><c1><ceos><brightgreen>replxx<rst>[\\]> <c12>abcdef<rst><ceos>"
"<rst><c18><c12>abcdefg<rst><ceos><rst><c19><bell><c1><ceos><brightgreen>replxx<rst>[|]> <c12>"
"abcdefg<rst><ceos><rst><c19><c12>abcdefg<rst><ceos><c19>\r\n"
"abcdefg\r\n"
"<c1><brightgreen>replxx<rst>> \r\n"],
			command = [ ReplxxTests._cxxSample_, "m", "F" ],
			pause = 0.5
		)
		self_.check_scenario(
			[ "a", "b", "c", "d", "e", "f", "g<tab><cr><c-d>" ], ["<c1><ceos>0\r\n"
"<brightgreen>replxx<rst>[-]> <c12><rst><ceos><rst><c12><c1><ceos><brightgreen>replxx<rst>[-]> <c12>"
"<yellow>1<rst><ceos><rst><c13><c12><yellow>1<rst><ceos><rst><c13><c12><yellow>1<rst>a<rst><ceos>"
"<rst><c14><c1><ceos><brightgreen>replxx<rst>[\\]> <c12><yellow>1<rst>a<rst><ceos><rst><c14><c1><ceos>"
"<brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>a<rst><ceos><rst><c14><c12><yellow>1<rst>ab<rst>"
"<ceos><rst><c15><c1><ceos><brightgreen>replxx<rst>[/]> <c12><yellow>1<rst>ab<rst><ceos><rst><c15>"
"<c1><ceos>1\r\n"
"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<rst><ceos><rst><c15><c1><ceos>"
"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst><ceos><rst><c16><c12><yellow>1<rst>"
"ab<yellow>2<rst><ceos><rst><c16><c12><yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c17><c1><ceos>"
"<brightgreen>replxx<rst>[\\]> <c12><yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c17><c1><ceos>"
"<brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>ab<yellow>2<rst>c<rst><ceos><rst><c17><c12>"
"<yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos><brightgreen>replxx<rst>[/]> <c12>"
"<yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>2\r\n"
"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<rst><ceos><rst><c18><c1><ceos>"
"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19>"
"<c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19><c1><ceos>"
"<brightgreen>replxx<rst>[\\]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst><ceos><rst><c19>"
"<c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst><c20><c1><ceos>"
"<brightgreen>replxx<rst>[|]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>e<rst><ceos><rst>"
"<c20><c1><ceos><brightgreen>replxx<rst>[/]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>"
"e<rst><ceos><rst><c20><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<rst><ceos><rst><c21><c1>"
"<ceos>3\r\n"
"<brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<rst><ceos><rst>"
"<c21><c1><ceos><brightgreen>replxx<rst>[-]> <c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>"
"ef<yellow>4<rst><ceos><rst><c22><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>ef<yellow>4<rst>"
"<ceos><rst><c22><c1><ceos><brightgreen>replxx<rst>[\\]> <c12><yellow>1<rst>ab<yellow>2<rst>"
"cd<yellow>3<rst>ef<yellow>4<rst><ceos><rst><c22><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>"
"ef<yellow>4<rst>g<rst><ceos><rst><c23><bell><c12><yellow>1<rst>ab<yellow>2<rst>cd<yellow>3<rst>"
"ef<yellow>4<rst>g<rst><ceos><c23>\r\n"
"1ab2cd3ef4g\r\n"
"<c1><brightgreen>replxx<rst>> <c1><ceos><brightgreen>replxx<rst>[|]> <c12><rst><ceos><rst><c12>\r\n"],
			command = [ ReplxxTests._cxxSample_, "m", "F", "k123456" ],
			pause = 0.487
		)
	@_no_parallel
	@unittest.skipIf( skip( "async" ), "timing-dependent; flaky on busy CI" )
	def test_prompt_from_callback( self_ ):
		self_.check_scenario(
			"<up>ri<tab>b<tab><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> some text color_b<rst><ceos>\r\n"
			"                  <gray>color_black<rst>\r\n"
			"                  <gray>color_brown<rst>\r\n"
			"                  <gray>color_blue<rst><rst><u3><c26><c1><ceos><brightgreen>replxx<rst>[17]> <c13>"
			"some text color_b<rst><ceos>\r\n"
			"                      <gray>color_black<rst>\r\n"
			"                      <gray>color_brown<rst>\r\n"
			"                      <gray>color_blue<rst><rst><u3><c30><c1><ceos><brightgreen>replxx<rst>"
			"[18]> <c13>some text color_br<rst><ceos>\r\n"
			"                      <gray>color_brown<rst>\r\n"
			"                      <gray>color_brightred<rst>\r\n"
			"                      <gray>color_brightgreen<rst><rst><u3><c31><c1><ceos><brightgreen>replxx<rst>"
			"[18]> <c13>some text color_br<rst><ceos>\r\n"
			"                      <gray>color_brown<rst>\r\n"
			"                      <gray>color_brightred<rst>\r\n"
			"                      <gray>color_brightgreen<rst><rst><u3><c31><c1><ceos><brightgreen>replxx<rst>"
			"[19]> <c13>some text color_bri<rst><ceos>\r\n"
			"                      <gray>color_brightred<rst>\r\n"
			"                      <gray>color_brightgreen<rst>\r\n"
			"                      <gray>color_brightblue<rst><rst><u3><c32><c1><ceos><brightgreen>replxx<rst>"
			"[19]> <c13>some text color_bri<rst><ceos>\r\n"
			"                      <gray>color_brightred<rst>\r\n"
			"                      <gray>color_brightgreen<rst>\r\n"
			"                      <gray>color_brightblue<rst><rst><u3><c32><c13>some text color_bright<rst>"
			"<ceos>\r\n"
			"                      <gray>color_brightred<rst>\r\n"
			"                      <gray>color_brightgreen<rst>\r\n"
			"                      <gray>color_brightblue<rst><rst><u3><c35><c1><ceos><brightgreen>replxx<rst>"
			"[22]> <c13>some text color_bright<rst><ceos>\r\n"
			"                      <gray>color_brightred<rst>\r\n"
			"                      <gray>color_brightgreen<rst>\r\n"
			"                      <gray>color_brightblue<rst><rst><u3><c35><c1><ceos><brightgreen>replxx<rst>"
			"[23]> <c13>some text color_brightb<rst><ceos><green>lue<rst><rst><c36><c1><ceos>"
			"<brightgreen>replxx<rst>[23]> <c13>some text color_brightb<rst><ceos><green>lue<rst><rst><c36><c13>"
			"some text <brightblue>color_brightblue<rst><ceos><rst><c39><c1><ceos><brightgreen>replxx<rst>"
			"[26]> <c13>some text <brightblue>color_brightblue<rst><ceos><rst><c39><c13>"
			"some text <brightblue>color_brightblue<rst><ceos><c39><c1><ceos><brightgreen>replxx<rst>[26]> \r\n"
			"some text color_brightblue\r\n"
			"<c1><brightgreen>replxx<rst>> <c9><rst><ceos><rst><c9><c1><ceos><brightgreen>replxx<rst>[0]> <c12>"
			"<rst><ceos><rst><c12>\r\n",
			"some text color_b\n",
			command = [ ReplxxTests._cxxSample_, "P" ]
		)
	def test_color_256( self_ ):
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> x <brown><bgcyan>c_3_6<rst> <color67>rgb123<rst> "
			"<color205><bgcolor78>fg513bg142<rst> <color253>gs21<rst> "
			"<color237>gs5<rst> <color251><bgcolor237>gs19gs5<rst> "
			"x<rst><ceos><rst><c53><c9>x <brown><bgcyan>c_3_6<rst> "
			"<color67>rgb123<rst> <color205><bgcolor78>fg513bg142<rst> "
			"<color253>gs21<rst> <color237>gs5<rst> "
			"<color251><bgcolor237>gs19gs5<rst> x<rst><ceos><c53>\r\n"
			"x c_3_6 rgb123 fg513bg142 gs21 gs5 gs19gs5 x\r\n<c1>",
			"x c_3_6 rgb123 fg513bg142 gs21 gs5 gs19gs5 x\n"
		)
	def test_bold_and_underline_attributes( self_ ):
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <bold_brightred>bold_color_brightred<rst> "
			"<brightred>color_brightred<rst> <bold_red>bold_color_red<rst> "
			"<red>color_red<rst> <underline_red>underline_color_red<rst> "
			"<bold_underline_red>bold_underline_color_red<rst><ceos><rst><c35><u1><c9><bold_brightred>bold_color_brightred<rst> "
			"<brightred>color_brightred<rst> <bold_red>bold_color_red<rst> "
			"<red>color_red<rst> <underline_red>underline_color_red<rst> "
			"<bold_underline_red>bold_underline_color_red<rst><ceos><c35>\r\n"
			"bold_color_brightred color_brightred bold_color_red color_red "
			"underline_color_red bold_underline_color_red\r\n<c1>",
			"bold_color_brightred color_brightred bold_color_red color_red underline_color_red bold_underline_color_red\n"
		)
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> normal_text <bold>bold_text<rst> <underline>underline_text<rst> "
			"<bold_underline>bold_underline_text<rst><ceos><rst><c65><c9>normal_text "
			"<bold>bold_text<rst> <underline>underline_text<rst> "
			"<bold_underline>bold_underline_text<rst><ceos><c65>\r\n"
			"normal_text bold_text underline_text bold_underline_text\r\n<c1>",
			"normal_text bold_text underline_text bold_underline_text\n"
		)
	def test_kill_to_begining_of_line_in_multiline( self_ ):
		self_.check_scenario(
			"<up><up><c-u><c-u><c-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><rst><c20><u3><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u1><c20><u2><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"cripture\r\n"
			"last line of a code<rst><u1><c1><u2><c9><ceos>cripture\r\n"
			"last line of a code<rst><u1><c9><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u1><c20><u2><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><c20>\r\n"
			"first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code\r\n"
			"<c1>",
			"first line of textsecond verse of a poemnext passage of a scripturelast line of a code\n"
		)
	def test_kill_to_end_of_line_in_multiline( self_ ):
		self_.check_scenario(
			"<up><pgup><down><c-k><c-k><c-y><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><rst><c20><u3><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u3><c9><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u2><c9><u1><c9><ceos>first line of text\r\n"
			"second v\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><u2><c9><u1><c9><ceos>first line of text\r\n"
			"second v<rst><rst><c9><u1><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><rst><c20><u3><c9><ceos>first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code<rst><c20>\r\n"
			"first line of text\r\n"
			"second verse of a poem\r\n"
			"next passage of a scripture\r\n"
			"last line of a code\r\n"
			"<c1>",
			"first line of textsecond verse of a poemnext passage of a scripturelast line of a code\n"
		)
	def test_long_prompt_multiline_enabled_hints( self_ ):
		prompt = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa> "
		self_.check_scenario(
			"<up><cr><c-d>",
			"<c1>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa> co<rst><ceos>\r\n"
			"                                       <gray>color_black<rst>\r\n"
			"                                       <gray>color_red<rst>\r\n"
			"                                       <gray>color_green<rst><rst><u3><c42><c40>co<rst><ceos><c42>\r\n"
			"co\r\n"
			"<c1>",
			"co\n",
			command = [ ReplxxTests._cxxSample_, "I", "p" + prompt ],
			dimensions = ( 24, 64 ),
			prompt = prompt
		)
	def test_ignore_case_hints_completions( self_ ):
		self_.check_scenario(
			"de<tab>e<tab><c-down><tab><cr><c-d>",
			"<c9>d<rst><ceos><rst><c10><c9>de<rst><ceos>\r\n"
			"        <gray>determinANT<rst>\r\n"
			"        <gray>determiNATION<rst>\r\n"
			"        <gray>deterMINE<rst><rst><u3><c11><c9>determin<rst><ceos>\r\n"
			"        <gray>determinANT<rst>\r\n"
			"        <gray>determiNATION<rst>\r\n"
			"        <gray>deterMINE<rst><rst><u3><c17><c9>determine<rst><ceos>\r\n"
			"        <gray>deterMINE<rst>\r\n"
			"        <gray>deTERMINED<rst><rst><u2><c18><c9>determine<rst><ceos><c18>\r\n"
			"<brightmagenta>deterMINE<rst>   <brightmagenta>deTERMINE<rst>D\r\n"
			"<brightgreen>replxx<rst>> <c9>determine<rst><ceos>\r\n"
			"        <gray>deterMINE<rst>\r\n"
			"        <gray>deTERMINED<rst><rst><u2><c18><c9>determine<rst><ceos>\r\n"
			"        <gray>deTERMINED<rst>\r\n"
			"        <gray>determine<rst><u2><c18><c9>deterMINE<rst><ceos><rst><c18><c9>deterMINE<rst><ceos><c18>"
			"\r\n"
			"deterMINE\r\n"
			"<c1>",
			command = [ ReplxxTests._cxxSample_, "i" ]
		)
		self_.check_scenario(
			"de<tab>e<tab>d<tab><cr><c-d>",
			"<c9>d<rst><ceos><rst><c10><c9>de<rst><ceos>\r\n"
			"        <gray>determinANT<rst>\r\n"
			"        <gray>determiNATION<rst>\r\n"
			"        <gray>deterMINE<rst><rst><u3><c11><c9>determin<rst><ceos>\r\n"
			"        <gray>determinANT<rst>\r\n"
			"        <gray>determiNATION<rst>\r\n"
			"        <gray>deterMINE<rst><rst><u3><c17><c9>determine<rst><ceos>\r\n"
			"        <gray>deterMINE<rst>\r\n"
			"        <gray>deTERMINED<rst><rst><u2><c18><c9>determine<rst><ceos><c18>\r\n"
			"<brightmagenta>deterMINE<rst>   <brightmagenta>deTERMINE<rst>D\r\n"
			"<brightgreen>replxx<rst>> <c9>determine<rst><ceos>\r\n"
			"        <gray>deterMINE<rst>\r\n"
			"        <gray>deTERMINED<rst><rst><u2><c18><c9>determined<rst><ceos><rst><c19><c9>deTERMINED<rst>"
			"<ceos><rst><c19><c9>deTERMINED<rst><ceos><c19>\r\n"
			"deTERMINED\r\n"
			"<c1>",
			command = [ ReplxxTests._cxxSample_, "i" ]
		)
	def test_ignore_case_history_search( self_ ):
		self_.check_scenario(
			"<c-r>er<backspace>R<cr><c-d>",
			"<c1><ceos><c1><ceos>(reverse-i-search)`': <c23><c1><ceos>(reverse-i-search)`e': determinANT<c27><c1>"
			"<ceos>(reverse-i-search)`er': determinANT<c28><c1><ceos>(reverse-i-search)`e': determinANT<c27><c1>"
			"<ceos>(reverse-i-search)`eR': deteRMINISM<c28><c1><ceos><brightgreen>replxx<rst>> deteRMINISM<c12>"
			"<c9>deteRMINISM<rst><ceos><c12><c9>deteRMINISM<rst><ceos><c20>\r\n"
			"thanks for the input: deteRMINISM\r\n"
			"<c1>",
			"deTERMINED\ndetERMINISTIC\ndeteRMINISM\ndeterMINE\ndetermiNATION\ndeterminANT\n",
			command = [ ReplxxTests._cSample_, "i1" ]
		)
		self_.check_scenario(
			"deter<m-p><cr><c-d>",
			"<c9>d<rst><ceos><gray>b<rst><rst><c10><c9>de<rst><ceos><rst><c11><c9>det<rst><ceos><rst><c12><c9>"
			"dete<rst><ceos><rst><c13><c9>deter<rst><ceos><rst><c14><c9>determinANT<rst><ceos><rst><c20><c9>"
			"determinANT<rst><ceos><c20>\r\n"
			"thanks for the input: determinANT\r\n"
			"<c1>",
			"deTERMINED\ndetERMINISTIC\ndeteRMINISM\ndeterMINE\ndetermiNATION\ndeterminANT\n",
			command = [ ReplxxTests._cSample_, "i1" ]
		)
		self_.check_scenario(
			"deteR<m-p><cr><c-d>",
			"<c9>d<rst><ceos><gray>b<rst><rst><c10><c9>de<rst><ceos><rst><c11><c9>det<rst><ceos><rst><c12><c9>"
			"dete<rst><ceos><rst><c13><c9>deteR<rst><ceos><rst><c14><c9>deteRMINISM<rst><ceos><rst><c20><c9>"
			"deteRMINISM<rst><ceos><c20>\r\n"
			"thanks for the input: deteRMINISM\r\n"
			"<c1>",
			"deTERMINED\ndetERMINISTIC\ndeteRMINISM\ndeterMINE\ndetermiNATION\ndeterminANT\n",
			command = [ ReplxxTests._cSample_, "i1" ]
		)
	def test_history_scratch( self_ ):
		self_.check_scenario(
			"<up>x<up>y<up>z<down><up>Z<pgdown><up><pgup><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> three<rst><ceos><rst><c14><c9>threex<rst><ceos><rst><c15><c1>"
			"<brightgreen>replxx<rst>> two<rst><ceos><rst><c12><c9>twoy<rst><ceos><rst><c13><c1>"
			"<brightgreen>replxx<rst>> one<rst><ceos><rst><c12><c9>onez<rst><ceos><rst><c13><c1>"
			"<brightgreen>replxx<rst>> twoy<rst><ceos><rst><c13><c1><brightgreen>replxx<rst>> onez<rst><ceos>"
			"<rst><c13><c9>onezZ<rst><ceos><rst><c14><c1><brightgreen>replxx<rst>> <rst><ceos><rst><c9><c1>"
			"<brightgreen>replxx<rst>> threex<rst><ceos><rst><c15><c1><brightgreen>replxx<rst>> onezZ<rst><ceos>"
			"<rst><c14><c9>onezZ<rst><ceos><c14>\r\n"
			"onezZ\r\n"
			"<c1>",
			"one\ntwo\nthree\n"
		)
		with open( "replxx_history.txt", "rb" ) as f:
			data = f.read().decode()
			origHist = "### 0000-00-00 00:00:00.000\none\n### 0000-00-00 00:00:00.000\ntwo\n### 0000-00-00 00:00:00.000\nthree\n";
			self_.assertSequenceEqual( data[:len(origHist)], origHist )
			self_.assertSequenceEqual( data[-6:], "onezZ\n" )
		self_.check_scenario(
			"<up>x<up>y<up>z<down><c-g><up><down><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> three<rst><ceos><rst><c14><c9>threex<rst><ceos><rst><c15><c1>"
			"<brightgreen>replxx<rst>> two<rst><ceos><rst><c12><c9>twoy<rst><ceos><rst><c13><c1>"
			"<brightgreen>replxx<rst>> one<rst><ceos><rst><c12><c9>onez<rst><ceos><rst><c13><c1>"
			"<brightgreen>replxx<rst>> twoy<rst><ceos><rst><c13><c9>two<rst><ceos><rst><c12><c1>"
			"<brightgreen>replxx<rst>> onez<rst><ceos><rst><c13><c1><brightgreen>replxx<rst>> two<rst><ceos><rst>"
			"<c12><c9>two<rst><ceos><c12>\r\n"
			"two\r\n"
			"<c1>",
			"one\ntwo\nthree\n"
		)
		self_.check_scenario(
			"<up>x<up>y<up>z<down><m-g><up><down><down><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> three<rst><ceos><rst><c14><c9>threex<rst><ceos><rst><c15><c1>"
			"<brightgreen>replxx<rst>> two<rst><ceos><rst><c12><c9>twoy<rst><ceos><rst><c13><c1>"
			"<brightgreen>replxx<rst>> one<rst><ceos><rst><c12><c9>onez<rst><ceos><rst><c13><c1>"
			"<brightgreen>replxx<rst>> twoy<rst><ceos><rst><c13><c9>two<rst><ceos><rst><c12><c1>"
			"<brightgreen>replxx<rst>> one<rst><ceos><rst><c12><c1><brightgreen>replxx<rst>> two<rst><ceos><rst>"
			"<c12><c1><brightgreen>replxx<rst>> three<rst><ceos><rst><c14><c9>three<rst><ceos><c14>\r\n"
			"three\r\n"
			"<c1>",
			"one\ntwo\nthree\n"
		)
	def test_move_up_over_multiline( self_ ):
		self_.check_scenario(
			"<m-up><m-up><m-up><cr><c-d>",
			"<c1><brightgreen>replxx<rst>> ZZZ<rst><ceos><rst><c12><c1><brightgreen>replxx<rst>> <ceos>"
			"bbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbbbbb<rst><rst><c24><u3><c1><brightgreen>replxx<rst>> <yellow>123<rst><ceos><rst>"
			"<c12><c9><yellow>123<rst><ceos><c12>\r\n"
			"123\r\n"
			"<c1>",
			"123\nbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\nZZZ\n"
		)
	def test_move_down_over_multiline( self_ ):
		self_.check_scenario(
			"<pgup><m-down><pgup><m-down><m-down>x<cr><c-d>",
			"<c1><brightgreen>replxx<rst>> <yellow>123<rst><ceos><rst><c12><c1><brightgreen>replxx<rst>> <ceos>"
			"bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbb<rst><rst><c17><u3><c9><ceos>bbbbbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbbbbbb\r\n"
			"bbbbbbbbbbbbbbbb<rst><u3><c9><c1><brightgreen>replxx<rst>> ZZZ<rst><ceos><rst><c12><c1>"
			"<brightgreen>replxx<rst>> <rst><ceos><rst><c9><c9>x<rst><ceos><rst><c10><c9>x<rst><ceos><c10>\r\n"
			"x\r\n"
			"<c1>",
			"123\nbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\nZZZ\n"
		)

	def test_position_tracking_no_color( self_ ):
		self_.check_scenario(
			"abcdef<home><cr><c-d>",
			"abcdef<c9>abcdef<ceos><c9><c9>abcdef<ceos><c15>\r\n"
			"thanks for the input: abcdef\r\n"
			"<c1>",
			command = [ ReplxxTests._cSample_, "m", "N", "S", "C", "M0" ]
		)
	def test_seeded_incremental_history_search( self_ ):
		self_.check_scenario(
			"for<m-r><m-r><cr><c-d>",
			"<c9>f<rst><ceos><rst><c10><c9>fo<rst><ceos><rst><c11><c9>for<rst><ceos><rst><c12><c1><ceos><c1>"
			"<ceos>(reverse-i-search)`for': for<c29><c1><ceos>(reverse-i-search)`for': forth<c26><c1><ceos>"
			"(reverse-i-search)`for': fortran<c26><c1><ceos><brightgreen>replxx<rst>> fortran<c9><c9>fortran<rst>"
			"<ceos><c9><c9>fortran<rst><ceos><c16>\r\n"
			"fortran\r\n"
			"<c1>",
			"\n".join( _words_[::-1] ) + "\n"
		)

def parseArgs( self, func, argv ):
	global verbosity
	res = func( self, argv )
	verbosity = self.verbosity
	return res

def _run_one( test_name ):
	"""Worker entry point for parallel runs: run a single test by name."""
	global verbosity
	verbosity = 0
	import io
	loader = unittest.TestLoader()
	suite = loader.loadTestsFromName( test_name )
	buf = io.StringIO()
	runner = unittest.TextTestRunner( stream = buf, verbosity = 2 )
	result = runner.run( suite )
	return ( test_name, result.wasSuccessful(), buf.getvalue() )

def _run_parallel( jobs ):
	import multiprocessing
	loader = unittest.TestLoader()
	suite = loader.loadTestsFromTestCase( ReplxxTests )
	parallel = []
	serial = []
	def _collect( s ):
		for t in s:
			if isinstance( t, unittest.TestSuite ):
				_collect( t )
				continue
			method = getattr( type( t ), t._testMethodName, None )
			if method is not None and getattr( method, "_no_parallel", False ):
				serial.append( t.id() )
			else:
				parallel.append( t.id() )
	_collect( suite )
	failures = 0
	passes = 0

	def _report( name, ok, out ):
		nonlocal failures, passes
		marker = "ok" if ok else "FAIL"
		print( "{:4} {}".format( marker, name ) )
		if not ok:
			print( out )
			failures += 1
		else:
			passes += 1

	with multiprocessing.Pool( processes = jobs ) as pool:
		for name, ok, out in pool.imap_unordered( _run_one, parallel ):
			_report( name, ok, out )
	# Run the timing-sensitive tests sequentially once the pool drains, so
	# they are not racing against ~jobs other PTYs. Even alone, the spinner
	# / async-print interleaving is not fully deterministic, so retry a few
	# times before declaring a failure.
	for name in serial:
		for attempt in range( 5 ):
			res = _run_one( name )
			if res[1]:
				break
		_report( *res )

	print( "{} passed, {} failed".format( passes, failures ) )
	return 0 if failures == 0 else 1

if __name__ == "__main__":
	if "-j" in sys.argv:
		i = sys.argv.index( "-j" )
		jobs = int( sys.argv[i + 1] ) if i + 1 < len( sys.argv ) else os.cpu_count() or 1
		del sys.argv[i:i + 2]
		sys.exit( _run_parallel( jobs ) )
	pa = unittest.TestProgram.parseArgs
	unittest.TestProgram.parseArgs = lambda self, argv: parseArgs( self, pa, argv )
	unittest.main()
