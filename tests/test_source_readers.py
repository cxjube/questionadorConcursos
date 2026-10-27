"""Synthetic fixtures only: never candidates for the study bank."""
import unittest

from tools.answer_tables import answer_table
from tools.reference_text import reference_text


class AnswerReaderTests(unittest.TestCase):
    def test_fgv_isolates_role_and_type_instead_of_overwriting_with_later_type(self):
        source = ('Analista Legislativo - Synthetic fixture - TIPO 1\n1 2 3\nA * E\n'
                  'Analista Legislativo - Synthetic fixture - TIPO 2\n1 2 3\nB C D\n')
        self.assertEqual(answer_table(source, 'Analista Legislativo - Synthetic fixture - TIPO 1'), {1:'A', 2:'X', 3:'E'})
        with self.assertRaises(ValueError):
            answer_table(source, 'Analista Legislativo - Different role - TIPO 1')

    def test_missing_or_repeated_exact_header_fails(self):
        header = 'Analista Legislativo - Synthetic fixture - TIPO 1'
        with self.assertRaises(ValueError): answer_table(header+'\n1\nA\n'+header+'\n1\nB', header)
        with self.assertRaises(ValueError): answer_table('Unrelated booklet\nItem 1\nGabarito C', 'Expected booklet')

    def test_truncated_duplicate_or_empty_answer_rows_fail(self):
        for text in ['Item 1 2\nGabarito C', 'Item 1\nGabarito C\nItem 1\nGabarito E', 'Item 1', 'No table']:
            with self.subTest(text=text), self.assertRaises(ValueError): answer_table('Fixture\n'+text, 'Fixture')

    def test_cebraspe_preserves_numbering_and_annulments(self):
        self.assertEqual(answer_table('Fixture\nItem 51 52 53\nGabarito C X E', 'Fixture'), {51:'C',52:'X',53:'E'})


class LegalReaderTests(unittest.TestCase):
    def test_excludes_scripts_styles_and_nested_struck_wording(self):
        html = b'<html><script>wrong</script><style>wrong</style><p><s>old <b>law</b></s>active <del>obsolete</del> clause.</p><p style="text-decoration: line-through">repealed</p><p>Next.</p></html>'
        self.assertEqual(reference_text(html), 'active clause. Next.')

    def test_declared_encoding_and_utf8_are_respected(self):
        self.assertEqual(reference_text('<meta charset="windows-1252"><p>A\xe7\xe3o</p>'.encode('windows-1252')), 'Ação')
        self.assertEqual(reference_text('<p>Constituição &amp; lei</p>'.encode()), 'Constituição & lei')

    def test_visible_parent_after_struck_child_is_not_dropped(self):
        self.assertEqual(reference_text(b'<p>before <strike><span>old</span></strike> after</p>'), 'before after')


class AlerjAnswerReaderTests(unittest.TestCase):
    def test_exact_role_type_and_morning_isolated_with_blank_layout_rows(self):
        header = 'Especialista Legislativo - Nível IV - Synthetic fixture - 1 - Turno Manhã'
        other = 'Especialista Legislativo - Nível IV - Synthetic fixture - 2 - Turno Manhã'
        later = 'Especialista Legislativo - Nível IV - Other fixture - 1 - Turno Manhã'
        source = header+'\n1 2 3\n\nD * E\n'+other+'\n1 2 3\nA B C\n'+later+'\n1 2 3\nC D A\n'
        self.assertEqual(answer_table(source, header), {1:'D', 2:'X', 3:'E'})
        with self.assertRaises(ValueError):
            answer_table(source, header.replace('Manhã', 'Tarde'))
        with self.assertRaises(ValueError):
            answer_table(source+'\n'+header+'\n1 2 3\nA B C', header)

    def test_blank_layout_rows_do_not_allow_missing_answers_or_text_to_masquerade_as_a_key(self):
        h = 'Especialista Legislativo - Nível IV - Synthetic fixture - 1 - Turno Manhã'
        for body in ['1 2\n\nA', '1\n\n', '1\n\nComment A', '1 2\n\n3 4\nA B', '1\nA\n1\nB']:
            with self.subTest(body=body), self.assertRaises(ValueError):
                answer_table(h+'\n'+body, h)


class PublisherEncodingFallbackTests(unittest.TestCase):
    def test_invalid_declared_charset_falls_back_to_strict_utf8_without_replacing_letters(self):
        raw=b'<meta charset="windows-1252"><p>'+ 'Árvore e divulgação pública'.encode('utf-8')+b'</p>'
        self.assertEqual(reference_text(raw),'Árvore e divulgação pública')

    def test_invalid_declared_and_invalid_utf8_bytes_are_not_silently_replaced(self):
        with self.assertRaises(UnicodeDecodeError):
            reference_text(b'<meta charset="windows-1252"><p>\x81\xff</p>')
