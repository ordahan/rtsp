'''
Created on Dec 14, 2013

@author: ord
'''
import unittest
from rtsp.message import RequestMessage, OptionsResponseMessage, \
    DescribeResponseMessage
from rtsp import directives
from rtsp import result_codes
from difflib import context_diff
import rtsp


class TestMessage(unittest.TestCase):

    def setUp(self):
        self.request = RequestMessage()

    def assertMessagesEqual(self, expected_message, actual_message):

        expected_message_lines = expected_message.split(rtsp.message.Message.NEWLINE)
        actual_message_lines = actual_message.split(rtsp.message.Message.NEWLINE)

        delta = context_diff(expected_message_lines,
                             actual_message_lines,
                             fromfile='expected',
                             tofile='actual',
                             lineterm=rtsp.message.Message.NEWLINE)

        try:
            starting_line = delta.next()
            raise AssertionError('\n' + starting_line + rtsp.message.Message.NEWLINE.join(delta))
        except StopIteration:
            pass

    def testInit(self):

        request_generated = RequestMessage(directives.OPTIONS, 13)

        self.assertEqual(directives.OPTIONS, request_generated.directive)
        self.assertEqual(13, request_generated.sequence)
        self.assertEqual('OPTIONS\n\rCSeq: 13',
                         str(request_generated))

class TestOptions(TestMessage):

    def testParse(self):
        '''
        Tests the parsing of the options message
        '''
        # Basic valid message
        message = \
            ''.join(
                    ['OPTIONS ' + \
                     'rtsp://localhost:10554/hello_world.avi RTSP/1.0\r\n',

                     'CSeq: 2\r\n',

                     'User-Agent: LibVLC/2.0.8 ' + \
                        '(LIVE555 Streaming Media v2011.12.23)\r\n',

                     '\r\n'])

        self.request.parse(message)

        self.assertEqual(2, self.request.sequence)
        self.assertEqual(directives.OPTIONS, self.request.directive)

    def testResponse(self):
        expected_response = \
            '\r\n'.join(["RTSP/1.0 200 OK",
                         "CSeq: 2",
                         "Content-Length: 0",
                         "Public: DESCRIBE,SETUP,TEARDOWN" +
                            ",PLAY,PAUSE,GET_PARAMETER",
                         '\r\n'])

        actual_response = str(OptionsResponseMessage(sequence=2,
                result=result_codes.OK))

        self.assertMessagesEqual(expected_response, actual_response)

class TestDescribe(TestMessage):

    def testParse(self):
        '''
        Tests the parsing of the describe message
        '''
        # Basic valid message
        message = \
            '\r\n'.join(['DESCRIBE rtsp://localhost:8554/homeland.avi RTSP/1.0',
                         'CSeq: 3',
                         'User-Agent: LibVLC/2.0.8 (LIVE555 Streaming Media v2011.12.23)',
                         'Accept: application/sdp',
                         '\r\n'])

        self.request.parse(message)

        self.assertEqual(3, self.request.sequence)
        self.assertEqual(directives.DESCRIBE, self.request.directive)

    def testResponse(self):

        date = 'Sun, 12 Jan 2014 13:04:23 GMT'
        uri = 'rtsp://127.0.0.1:18554/homeland.avi'
        length = 509
        sdp_o_param = 15455528565056244265

        expected_response = \
            '\r\n'.join([
                       'RTSP/1.0 200 OK',
                       'CSeq: 3',
                       'Content-Length: %d' % length,
                       'Server: VLC/2.0.8',
                       'Date: %s' % date,
                       'Content-Type: application/sdp',
                       'Content-Base: %s' % uri,
                       'Cache-Control: no-cache',
                       '',
                       'v=0',
                       'o=- {time} {time} IN IP4 desktop'.format(time=sdp_o_param),
                       's=Unnamed',
                       'i=N/A',
                       'c=IN IP4 0.0.0.0',
                       't=0 0',
                       'a=tool:vlc 2.0.8',
                       'a=recvonly',
                       'a=type:broadcast',
                       'a=charset:UTF-8',
                       'a=control:%s' % uri,
                       'm=video 0 RTP/AVP 96',
                       'b=RR:0',
                       'a=rtpmap:96 H264/90000',
                       'a=fmtp:96 packetization-mode=1;profile-level-id=64001f;sprop-parameter-sets=Z2QAH6zZgLQz+sBagQEAoAAAfSAAF3AR4wYzQA==,aOl4fLIs;',
                       'a=control:%s/trackID=0' % uri,
                       'm=audio 0 RTP/AVP 8',
                       'b=RR:0',
                       'a=control:%s/trackID=1' % uri,
                        '\r\n'])

        actual_response = str(DescribeResponseMessage(sequence=3,
                                                      result=result_codes.OK,
                                                      date=date,
                                                      uri=uri,
                                                      sdp_o_param=sdp_o_param))

        self.assertMessagesEqual(expected_response, actual_response)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'TestMessage.testOptions']
    unittest.main()
