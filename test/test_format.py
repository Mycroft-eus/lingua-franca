#
# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import unittest
import datetime
import ast
import warnings
import sys
from pathlib import Path

# TODO either write a getter for lingua_franca.internal._SUPPORTED_LANGUAGES,
# or make it public somehow
from lingua_franca import load_languages, unload_languages, set_default_lang, \
    get_primary_lang_code, get_active_langs, get_supported_langs
from lingua_franca.internal import UnsupportedLanguageError
from lingua_franca.format import nice_number
from lingua_franca.format import nice_time
from lingua_franca.format import nice_date
from lingua_franca.format import nice_date_time
from lingua_franca.format import nice_year
from lingua_franca.format import nice_duration
from lingua_franca.format import pronounce_number
from lingua_franca.format import date_time_format
from lingua_franca.format import join_list
from lingua_franca.format import nice_relative_time
from lingua_franca.time import default_timezone


def setUpModule():
    load_languages(get_supported_langs())
    # TODO spin English tests off into another file, like other languages, so we
    # don't have to do this confusing thing in the "master" test_format.py
    set_default_lang('en-us')


def tearDownModule():
    unload_languages(get_active_langs())


NUMBERS_FIXTURE_EN = {
    1.435634: '1.436',
    2: '2',
    5.0: '5',
    0.027: '0.027',
    0.5: 'a half',
    1.333: '1 and a third',
    2.666: '2 and 2 thirds',
    0.25: 'a forth',
    1.25: '1 and a forth',
    0.75: '3 forths',
    1.75: '1 and 3 forths',
    3.4: '3 and 2 fifths',
    16.8333: '16 and 5 sixths',
    12.5714: '12 and 4 sevenths',
    9.625: '9 and 5 eigths',
    6.777: '6 and 7 ninths',
    3.1: '3 and a tenth',
    2.272: '2 and 3 elevenths',
    5.583: '5 and 7 twelveths',
    8.384: '8 and 5 thirteenths',
    0.071: 'a fourteenth',
    6.466: '6 and 7 fifteenths',
    8.312: '8 and 5 sixteenths',
    2.176: '2 and 3 seventeenths',
    200.722: '200 and 13 eighteenths',
    7.421: '7 and 8 nineteenths',
    0.05: 'a twentyith'
}


class TestNiceNumberFormat(unittest.TestCase):

    tmp_var = None

    def set_tmp_var(self, val):
        self.tmp_var = val

    def test_convert_float_to_nice_number(self):
        for number, number_str in NUMBERS_FIXTURE_EN.items():
            self.assertEqual(nice_number(number), number_str,
                             'should format {} as {} and not {}'.format(
                                 number, number_str, nice_number(number)))

    def test_specify_denominator(self):
        self.assertEqual(nice_number(5.5, denominators=[1, 2, 3]),
                         '5 and a half',
                         'should format 5.5 as 5 and a half not {}'.format(
                             nice_number(5.5, denominators=[1, 2, 3])))
        self.assertEqual(nice_number(2.333, denominators=[1, 2]),
                         '2.333',
                         'should format 2.333 as 2.333 not {}'.format(
                             nice_number(2.333, denominators=[1, 2])))

    def test_no_speech(self):
        self.assertEqual(nice_number(6.777, speech=False),
                         '6 7/9',
                         'should format 6.777 as 6 7/9 not {}'.format(
                             nice_number(6.777, speech=False)))
        self.assertEqual(nice_number(6.0, speech=False),
                         '6',
                         'should format 6.0 as 6 not {}'.format(
                             nice_number(6.0, speech=False)))

    def test_unknown_language(self):
        """ An unknown / unhandled language should return the string
            representation of the input number.
        """
        def bypass_warning():
            self.assertEqual(
                nice_number(5.5, lang='as-df'), '5.5',
                'should format 5.5 '
                'as 5.5 not {}'.format(
                    nice_number(5.5, lang='as-df')))

        # Should throw a warning. Would raise the same text as a
        # NotImplementedError, but nice_number() bypasses and returns
        # its input as a string
        self.assertWarns(UserWarning, bypass_warning)


class TestPronounceNumber(unittest.TestCase):
    def test_convert_int(self):
        self.assertEqual(pronounce_number(0), "zero")
        self.assertEqual(pronounce_number(1), "one")
        self.assertEqual(pronounce_number(10), "ten")
        self.assertEqual(pronounce_number(15), "fifteen")
        self.assertEqual(pronounce_number(20), "twenty")
        self.assertEqual(pronounce_number(27), "twenty seven")
        self.assertEqual(pronounce_number(30), "thirty")
        self.assertEqual(pronounce_number(33), "thirty three")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1), "minus one")
        self.assertEqual(pronounce_number(-10), "minus ten")
        self.assertEqual(pronounce_number(-15), "minus fifteen")
        self.assertEqual(pronounce_number(-20), "minus twenty")
        self.assertEqual(pronounce_number(-27), "minus twenty seven")
        self.assertEqual(pronounce_number(-30), "minus thirty")
        self.assertEqual(pronounce_number(-33), "minus thirty three")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(0.05), "zero point zero five")
        self.assertEqual(pronounce_number(-0.05), "minus zero point zero five")
        self.assertEqual(pronounce_number(1.234),
                         "one point two three")
        self.assertEqual(pronounce_number(21.234),
                         "twenty one point two three")
        self.assertEqual(pronounce_number(21.234, places=1),
                         "twenty one point two")
        self.assertEqual(pronounce_number(21.234, places=0),
                         "twenty one")
        self.assertEqual(pronounce_number(21.234, places=3),
                         "twenty one point two three four")
        self.assertEqual(pronounce_number(21.234, places=4),
                         "twenty one point two three four")
        self.assertEqual(pronounce_number(21.234, places=5),
                         "twenty one point two three four")
        self.assertEqual(pronounce_number(-1.234),
                         "minus one point two three")
        self.assertEqual(pronounce_number(-21.234),
                         "minus twenty one point two three")
        self.assertEqual(pronounce_number(-21.234, places=1),
                         "minus twenty one point two")
        self.assertEqual(pronounce_number(-21.234, places=0),
                         "minus twenty one")
        self.assertEqual(pronounce_number(-21.234, places=3),
                         "minus twenty one point two three four")
        self.assertEqual(pronounce_number(-21.234, places=4),
                         "minus twenty one point two three four")
        self.assertEqual(pronounce_number(-21.234, places=5),
                         "minus twenty one point two three four")

    def test_convert_hundreds(self):
        self.assertEqual(pronounce_number(100), "one hundred")
        self.assertEqual(pronounce_number(666), "six hundred and sixty six")
        self.assertEqual(pronounce_number(1456), "fourteen fifty six")
        self.assertEqual(pronounce_number(103254654), "one hundred and three "
                                                      "million, two hundred "
                                                      "and fifty four "
                                                      "thousand, six hundred "
                                                      "and fifty four")
        self.assertEqual(pronounce_number(1512457), "one million, five hundred"
                                                    " and twelve thousand, "
                                                    "four hundred and fifty "
                                                    "seven")
        self.assertEqual(pronounce_number(209996), "two hundred and nine "
                                                   "thousand, nine hundred "
                                                   "and ninety six")

    def test_convert_scientific_notation(self):
        self.assertEqual(pronounce_number(0, scientific=True), "zero")
        self.assertEqual(pronounce_number(33, scientific=True),
                         "three point three times ten to the power of one")
        self.assertEqual(pronounce_number(299792458, scientific=True),
                         "two point nine nine times ten to the power of eight")
        self.assertEqual(pronounce_number(299792458, places=6,
                                          scientific=True),
                         "two point nine nine seven nine two five times "
                         "ten to the power of eight")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True),
                         "one point six seven two times ten to the power of "
                         "negative twenty seven")

    def test_auto_scientific_notation(self):
        self.assertEqual(
            pronounce_number(1.1e-150), "one point one times ten to the "
                                        "power of negative one hundred "
                                        "and fifty")
        # value is platform dependent so better not use in tests?
        # self.assertEqual(
        #    pronounce_number(sys.float_info.min), "two point two two times "
        #                                          "ten to the power of "
        #                                          "negative three hundred "
        #                                          "and eight")
        # self.assertEqual(
        #    pronounce_number(sys.float_info.max), "one point seven nine "
        #                                          "times ten to the power of"
        #                                          " three hundred and eight")

    def test_large_numbers(self):
        self.assertEqual(
            pronounce_number(299792458, short_scale=True),
            "two hundred and ninety nine million, seven hundred "
            "and ninety two thousand, four hundred and fifty eight")
        self.assertEqual(
            pronounce_number(299792458, short_scale=False),
            "two hundred and ninety nine million, seven hundred "
            "and ninety two thousand, four hundred and fifty eight")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=True),
            "one hundred quintillion, thirty four quadrillion, "
            "two hundred and ninety nine million, seven hundred "
            "and ninety two thousand, four hundred and fifty eight")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=False),
            "one hundred trillion, thirty four thousand billion, "
            "two hundred and ninety nine million, seven hundred "
            "and ninety two thousand, four hundred and fifty eight")
        self.assertEqual(
            pronounce_number(10000000000, short_scale=True),
            "ten billion")
        self.assertEqual(
            pronounce_number(1000000000000, short_scale=True),
            "one trillion")
        # TODO maybe beautify this
        self.assertEqual(
            pronounce_number(1000001, short_scale=True),
            "one million, one")
        self.assertEqual(pronounce_number(95505896639631893),
                         "ninety five quadrillion, five hundred and five "
                         "trillion, eight hundred and ninety six billion, six "
                         "hundred and thirty nine million, six hundred and "
                         "thirty one thousand, eight hundred and ninety three")
        self.assertEqual(pronounce_number(95505896639631893,
                                          short_scale=False),
                         "ninety five thousand five hundred and five billion, "
                         "eight hundred and ninety six thousand six hundred "
                         "and thirty nine million, six hundred and thirty one "
                         "thousand, eight hundred and ninety three")
        self.assertEqual(pronounce_number(10e80, places=1),
                         "one qesvigintillion")
        # TODO floating point rounding issues might happen
        self.assertEqual(pronounce_number(1.9874522571e80, places=9),
                         "one hundred and ninety eight quinquavigintillion, "
                         "seven hundred and forty five quattuorvigintillion, "
                         "two hundred and twenty five tresvigintillion, "
                         "seven hundred and nine uuovigintillion, "
                         "nine hundred and ninety nine unvigintillion, "
                         "nine hundred and eighty nine vigintillion, "
                         "seven hundred and thirty novendecillion, nine "
                         "hundred and nineteen octodecillion, nine hundred "
                         "and ninety nine septendecillion, nine hundred "
                         "and fifty five sedecillion, four hundred and "
                         "ninety eight quinquadecillion, two hundred and "
                         "fourteen quattuordecillion, eight hundred and "
                         "forty five tredecillion, four hundred and "
                         "twenty nine duodecillion, four hundred and "
                         "forty four undecillion, three hundred and "
                         "thirty six decillion, seven hundred and twenty "
                         "four nonillion, five hundred and sixty nine "
                         "octillion, three hundred and seventy five "
                         "septillion, two hundred and thirty nine sextillion,"
                         " six hundred and seventy quintillion, five hundred "
                         "and seventy four quadrillion, seven hundred and "
                         "thirty nine trillion, seven hundred and forty "
                         "eight billion, four hundred and seventy million, "
                         "nine hundred and fifteen thousand, seventy two")
        self.assertEqual(pronounce_number(1.00000000000000001e150),
                         "nine hundred and ninety nine millinillion, nine "
                         "hundred and ninety nine uncentillion, nine hundred "
                         "and ninety nine centillion, nine hundred and ninety"
                         " nine nonagintillion, nine hundred and ninety nine"
                         " octogintillion, nine hundred and eighty"
                         " septuagintillion, eight hundred and thirty five "
                         "sexagintillion, five hundred and ninety six "
                         "quinquagintillion, one hundred and seventy two"
                         " quadragintillion, four hundred and thirty seven"
                         " noventrigintillion, three hundred and seventy four"
                         " octotrigintillion, five hundred and ninety"
                         " septentrigintillion, five hundred and seventy"
                         " three sestrigintillion, one hundred and twenty "
                         "quinquatrigintillion, fourteen quattuortrigintillion"
                         ", thirty trestrigintillion, three hundred and "
                         "eighteen duotrigintillion, seven hundred and ninety"
                         " three untrigintillion, ninety one trigintillion,"
                         " one hundred and sixty four novemvigintillion, eight"
                         " hundred and ten octovigintillion, one hundred and"
                         " fifty four septemvigintillion, one hundred "
                         "qesvigintillion, one hundred and twelve "
                         "quinquavigintillion, two hundred and three "
                         "quattuorvigintillion, six hundred and seventy "
                         "eight tresvigintillion, five hundred and eighty "
                         "two uuovigintillion, nine hundred and seventy six"
                         " unvigintillion, two hundred and ninety eight "
                         "vigintillion, two hundred and sixty eight "
                         "novendecillion, six hundred and sixteen "
                         "octodecillion, two hundred and twenty one "
                         "septendecillion, one hundred and fifty one"
                         " sedecillion, nine hundred and sixty two "
                         "quinquadecillion, seven hundred and two"
                         " quattuordecillion, sixty tredecillion, two hundred"
                         " and sixty six duodecillion, one hundred and "
                         "seventy six undecillion, five decillion, four "
                         "hundred and forty nonillion, five hundred and"
                         " sixty seven octillion, thirty two septillion, "
                         "three hundred and thirty one sextillion, "
                         "two hundred and eight quintillion, four hundred and "
                         "three quadrillion, nine hundred and forty eight "
                         "trillion, two hundred and thirty three billion, "
                         "three hundred and seventy three million, five "
                         "hundred and fifteen thousand, seven hundred and "
                         "seventy six")

        # infinity
        self.assertEqual(
            pronounce_number(sys.float_info.max * 2), "infinity")
        self.assertEqual(
            pronounce_number(float("inf")),
            "infinity")
        self.assertEqual(
            pronounce_number(float("-inf")),
            "negative infinity")

    def test_ordinals(self):
        self.assertEqual(pronounce_number(1, ordinals=True), "first")
        self.assertEqual(pronounce_number(10, ordinals=True), "tenth")
        self.assertEqual(pronounce_number(15, ordinals=True), "fifteenth")
        self.assertEqual(pronounce_number(20, ordinals=True), "twentieth")
        self.assertEqual(pronounce_number(27, ordinals=True), "twenty seventh")
        self.assertEqual(pronounce_number(30, ordinals=True), "thirtieth")
        self.assertEqual(pronounce_number(33, ordinals=True), "thirty third")
        self.assertEqual(pronounce_number(100, ordinals=True), "hundredth")
        self.assertEqual(pronounce_number(1000, ordinals=True), "thousandth")
        self.assertEqual(pronounce_number(10000, ordinals=True),
                         "ten thousandth")
        self.assertEqual(pronounce_number(18691, ordinals=True),
                         "eighteen thousand, six hundred and ninety first")
        self.assertEqual(pronounce_number(1567, ordinals=True),
                         "one thousand, five hundred and sixty seventh")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True, ordinals=True),
                         "one point six seven two times ten to the negative "
                         "twenty seventh power")
        self.assertEqual(pronounce_number(18e6, ordinals=True),
                         "eighteen millionth")
        self.assertEqual(pronounce_number(18e12, ordinals=True,
                                          short_scale=False),
                         "eighteen billionth")
        self.assertEqual(pronounce_number(18e12, ordinals=True),
                         "eighteen trillionth")
        self.assertEqual(pronounce_number(18e18, ordinals=True,
                                          short_scale=False), "eighteen "
                                                              "trillionth")

# def nice_time(dt, lang="en-us", speech=True, use_24hour=False,
#              use_ampm=False):


class TestNiceDateFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read date_time_test.json files for test data
        cls.test_config = {}
        p = Path(date_time_format.config_path)
        for sub_dir in [x for x in p.iterdir() if x.is_dir()]:
            if (sub_dir / 'date_time_test.json').exists():
                print("Getting test for " +
                      str(sub_dir / 'date_time_test.json'))
                with (sub_dir / 'date_time_test.json').open() as f:
                    cls.test_config[sub_dir.parts[-1]] = json.loads(f.read())

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31, 
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt),
                         nice_time(dt, "en-us", True, False, False))

        self.assertEqual(nice_time(dt),
                         "one twenty two")

        self.assertEqual(nice_time(dt, use_ampm=True),
                         "one twenty two p.m.")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "thirteen twenty two")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "thirteen twenty two")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "one o'clock")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "one p.m.")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "thirteen hundred")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "thirteen hundred")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "one oh two")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "one oh two p.m.")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "thirteen zero two")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "thirteen zero two")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "twelve oh two")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "twelve oh two a.m.")
        self.assertEqual(nice_time(dt, speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "zero zero zero two")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "zero zero zero two")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "one oh two")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "one oh two a.m.")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:02 AM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "zero one zero two")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "zero one zero two")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "quarter past twelve")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "quarter past twelve p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "half past five a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "quarter to two")

    def test_nice_date(self):
        for lang in self.test_config:
            i = 1
            while (self.test_config[lang].get('test_nice_date') and
                   self.test_config[lang]['test_nice_date'].get(str(i))):
                p = self.test_config[lang]['test_nice_date'][str(i)]
                dp = ast.literal_eval(p['datetime_param'])
                np = ast.literal_eval(p['now'])
                dt = datetime.datetime(
                    dp[0], dp[1], dp[2], dp[3], dp[4], dp[5])
                now = None if not np else datetime.datetime(
                    np[0], np[1], np[2], np[3], np[4], np[5])
                print('Testing for ' + lang + ' that ' + str(dt) +
                      ' is date ' + p['assertEqual'])
                self.assertEqual(p['assertEqual'],
                                 nice_date(dt, lang=lang, now=now))
                i = i + 1

        # test all days in a year for all languages,
        # that some output is produced
        for lang in self.test_config:
            for dt in (datetime.datetime(2017, 12, 30, 0, 2, 3) +
                       datetime.timedelta(n) for n in range(368)):
                self.assertTrue(len(nice_date(dt, lang=lang)) > 0)

    def test_nice_date_time(self):
        # TODO: migrate these tests (in res files) to respect the new
        # language loading features. Right now, some of them break if
        # their languages are not default.
        for lang in self.test_config:
            set_default_lang(lang)
            i = 1
            while (self.test_config[lang].get('test_nice_date_time') and
                   self.test_config[lang]['test_nice_date_time'].get(str(i))):
                p = self.test_config[lang]['test_nice_date_time'][str(i)]
                dp = ast.literal_eval(p['datetime_param'])
                np = ast.literal_eval(p['now'])
                dt = datetime.datetime(
                    dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                    tzinfo=default_timezone())
                now = None if not np else datetime.datetime(
                    np[0], np[1], np[2], np[3], np[4], np[5],
                    tzinfo=default_timezone())
                print('Testing for ' + lang + ' that ' + str(dt) +
                      ' is date time ' + p['assertEqual'])
                self.assertEqual(
                    p['assertEqual'],
                    nice_date_time(
                        dt, lang=lang, now=now,
                        use_24hour=ast.literal_eval(p['use_24hour']),
                        use_ampm=ast.literal_eval(p['use_ampm'])))
                i = i + 1
        set_default_lang('en')

    def test_nice_year(self):
        for lang in self.test_config:
            i = 1
            while (self.test_config[lang].get('test_nice_year') and
                   self.test_config[lang]['test_nice_year'].get(str(i))):
                p = self.test_config[lang]['test_nice_year'][str(i)]
                dp = ast.literal_eval(p['datetime_param'])
                dt = datetime.datetime(
                    dp[0], dp[1], dp[2], dp[3], dp[4], dp[5])
                print('Testing for ' + lang + ' that ' + str(dt) +
                      ' is year ' + p['assertEqual'])
                self.assertEqual(p['assertEqual'], nice_year(
                    dt, lang=lang, bc=ast.literal_eval(p['bc'])))
                i = i + 1

        # Test all years from 0 to 9999 for all languages,
        # that some output is produced
        for lang in self.test_config:
            print("Test all years in " + lang)
            for i in range(1, 9999):
                dt = datetime.datetime(i, 1, 31, 13, 2, 3, tzinfo=default_timezone())
                self.assertTrue(len(nice_year(dt, lang=lang)) > 0)
                # Looking through the date sequence can be helpful

#                print(nice_year(dt, lang=lang))

    def test_nice_duration(self):
        self.assertEqual(nice_duration(1), "one second")
        self.assertEqual(nice_duration(3), "three seconds")
        self.assertEqual(nice_duration(1, speech=False), "0:01")
        self.assertEqual(nice_duration(61), "one minute one second")
        self.assertEqual(nice_duration(61, speech=False), "1:01")
        self.assertEqual(nice_duration(5000),
                         "one hour twenty three minutes twenty seconds")
        self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000),
                         "thirteen hours fifty three minutes twenty seconds")
        self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000),
                         "five days  eighteen hours fifty three minutes twenty seconds")  # nopep8
        self.assertEqual(nice_duration(500000, speech=False), "5d 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
                                       speech=False),
                         "5d 18:53:20")

    def test_join(self):
        self.assertEqual(join_list(None, "and"), "")
        self.assertEqual(join_list([], "and"), "")

        self.assertEqual(join_list(["a"], "and"), "a")
        self.assertEqual(join_list(["a", "b"], "and"), "a and b")
        self.assertEqual(join_list(["a", "b"], "or"), "a or b")

        self.assertEqual(join_list(["a", "b", "c"], "and"), "a, b and c")
        self.assertEqual(join_list(["a", "b", "c"], "or"), "a, b or c")
        self.assertEqual(join_list(["a", "b", "c"], "or", ";"), "a; b or c")
        self.assertEqual(join_list(["a", "b", "c", "d"], "or"), "a, b, c or d")

        self.assertEqual(join_list([1, "b", 3, "d"], "or"), "1, b, 3 or d")


class TestNiceRelativeTime(unittest.TestCase):
    def test_format_nice_relative_time(self):
        base_datetime = datetime.datetime(2017, 1, 31, 13, 22, 3,
                            tzinfo=default_timezone())
        two_hours_from_base = base_datetime + datetime.timedelta(hours=2)
        self.assertEqual(
            nice_relative_time(when=two_hours_from_base, relative_to=base_datetime),
            "2 hours"
        )
        twoish_hours_from_base = base_datetime + datetime.timedelta(hours=2, minutes=27)
        self.assertEqual(
            nice_relative_time(when=twoish_hours_from_base, relative_to=base_datetime),
            "2 hours"
        )
        seconds_from_base = base_datetime + datetime.timedelta(seconds=47)
        self.assertEqual(
            nice_relative_time(when=seconds_from_base, relative_to=base_datetime),
            "47 seconds"
        )
        three_days_from_base = base_datetime + datetime.timedelta(days=3)
        self.assertEqual(
            nice_relative_time(when=three_days_from_base, relative_to=base_datetime),
            "3 days"
        )
        almost_four_days_from_base = base_datetime + datetime.timedelta(days=3, hours=20)
        self.assertEqual(
            nice_relative_time(when=almost_four_days_from_base, relative_to=base_datetime),
            "4 days"
        )
        long_time_from_base = base_datetime + datetime.timedelta(days=957, hours=2, seconds=12)
        self.assertEqual(
            nice_relative_time(when=long_time_from_base, relative_to=base_datetime),
            "957 days"
        )


if __name__ == "__main__":
    unittest.main()
