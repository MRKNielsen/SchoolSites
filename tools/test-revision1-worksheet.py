#!/usr/bin/env python3
"""Negative tests for the Revision 1 worksheet's answer-copy check.

    python3 tools/test-revision1-worksheet.py

revision1_worksheet.py's verify() claims that stripping the red overlay
off the answer copy gives the student sheet back exactly, and that every
slot a student writes in is filled. This asserts that the check can
actually fail: it breaks each defect class in turn and requires verify()
to raise.

That matters because the rubric build shipped once with ~12,600 characters
spliced out and a passing check — the check only exercised the part of the
file that survived. A check nobody has seen fail is not evidence.
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    'revision1_worksheet', os.path.join(HERE, 'revision1_worksheet.py'))
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

STUDENT = w.student_page(w.build(False))
GOOD = w.answer_payload(w.build(True))

CASES = {
    'answer ate the question wording':
        lambda s: s.replace('Which place, P or Q, is in daylight right now?', '', 1),
    'a question dropped from the answer copy':
        lambda s: re.sub(r'<div class="q"><span class="qn">5</span>.*?</div>\n    </div>',
                         '', s, 1, re.S),
    'a ruled block left unfilled':
        lambda s: s.replace('<div class="lines filled" data-lines="3">',
                            '<div class="lines" data-lines="3">', 1),
    'an inline blank left unfilled':
        lambda s: s.replace('<span class="blank lg"><span class="wsa-in">24 hours</span></span>',
                            '<span class="blank lg"></span>', 1),
    'line count changed under the answer':
        lambda s: s.replace('<div class="lines filled" data-lines="3">',
                            '<div class="lines filled" data-lines="2">', 1),
    'the model diagram missing from Part 10':
        lambda s: s.replace('<figure class="ws-fig" data-h="lg">',
                            '<figure class="ws-fig" data-h="md">', 1),
    'an exit cell filled in that should not be':
        lambda s: s.replace('<td class="fill"></td>',
                            '<td class="fill"><span class="wsa-in">Confident</span></td>', 1),
}


def main():
    # The good build must pass, or every negative below is meaningless.
    w.verify(STUDENT, GOOD)

    bad = []
    for name, break_it in CASES.items():
        broken = break_it(GOOD)
        assert broken != GOOD, f'test case did not change anything: {name}'
        try:
            w.verify(STUDENT, broken)
        except AssertionError:
            print(f'  caught   {name}')
            continue
        print(f'  MISSED   {name}')
        bad.append(name)

    if bad:
        print(f'\n{len(bad)} defect class(es) go undetected: ' + ', '.join(bad))
        return 1
    print(f'\nall {len(CASES)} defect classes caught')
    return 0


if __name__ == '__main__':
    sys.exit(main())
