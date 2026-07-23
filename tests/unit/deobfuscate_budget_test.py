"""Tests for the optional wall-clock budget on deobfuscation (TKT-16478).

The budget is deliberately coarse: it is checked inline between outer transform
cycles (never via exceptions, which the pipeline's broad ``except Exception``
handlers would swallow). On expiry the best result so far is returned. The
budget restarts at each nested decode layer (JSFuck/eval-packed recursion).
"""

from unittest.mock import MagicMock
from unittest.mock import patch

import pyjsclear
from pyjsclear.deobfuscator import Deobfuscator


class TestDeobfuscateBudget:
    def test_deobfuscate_accepts_a_time_budget_and_returns_a_string(self):
        # Budget is honored between outer cycles; a tiny budget still returns valid source.
        out = pyjsclear.deobfuscate('var a=1;var b=2;console.log(a+b);', time_budget_seconds=0.001)
        assert isinstance(out, str)
        assert out

    def test_deobfuscate_file_accepts_a_time_budget(self, tmp_path):
        input_file = tmp_path / 'input.js'
        input_file.write_text('var x = 1;')

        result = pyjsclear.deobfuscate_file(str(input_file), time_budget_seconds=0.001)
        assert isinstance(result, str)


class TestDeobfuscatorBudgetInternals:
    def test_budget_defaults_to_none_and_is_stored_when_given(self):
        assert Deobfuscator('var x = 1;').time_budget_seconds is None
        assert Deobfuscator('var x = 1;', time_budget_seconds=2.5).time_budget_seconds == 2.5

    def test_budget_expiry_mid_loop_stops_after_one_cycle_and_returns_source(self):
        # Deterministic mid-loop expiry: fake the clock so the budget check
        # passes at cycle 0 and trips at cycle 1. Expected monotonic() calls on
        # this path (verified against deobfuscator.py, the only module using
        # time): start capture -> 0.0, cycle-0 check -> 0.0, cycle-1 check ->
        # 10.0. The `time` attribute is patched in the deobfuscator module
        # namespace only, so nothing else consumes the side_effect values.
        fake_time = MagicMock()
        fake_time.monotonic.side_effect = [0.0, 0.0, 10.0]
        deobfuscator = Deobfuscator('var a = 1; var b = a; console.log(b);', time_budget_seconds=5.0)

        with (
            patch.object(Deobfuscator, '_run_ast_transforms', return_value=True) as run_transforms_mock,
            patch('pyjsclear.deobfuscator.time', fake_time),
        ):
            result = deobfuscator.execute()

        # Exactly one transform cycle ran before the budget expired.
        assert run_transforms_mock.call_count == 1
        # All three clock reads happened: the cycle-1 check executed and
        # tripped (i.e. the loop did not end early for another reason).
        assert fake_time.monotonic.call_count == 3
        assert isinstance(result, str)
        assert result

    def test_exhausted_budget_skips_transform_cycles_entirely(self):
        # The check sits at the top of each outer cycle: a zero budget is
        # already expired at cycle 0, so no transform cycle should run at all,
        # yet execute() must still return valid source (best-so-far path).
        deobfuscator = Deobfuscator('var a = 1; var b = a; console.log(b);', time_budget_seconds=0.0)

        with patch.object(Deobfuscator, '_run_ast_transforms', return_value=False) as run_transforms_mock:
            result = deobfuscator.execute()

        run_transforms_mock.assert_not_called()
        assert isinstance(result, str)
        assert result

    def test_recursive_pre_pass_deobfuscator_inherits_the_budget(self):
        # When a pre-pass decodes a nested layer (JSFuck/eval-packed), the
        # recursively constructed Deobfuscator must receive the same budget.
        outer = Deobfuscator('outer code', time_budget_seconds=1.5)
        nested = MagicMock()
        nested.execute.return_value = 'const x = 1;'

        with (
            patch.object(Deobfuscator, '_run_pre_passes', return_value='var x = 1;'),
            patch('pyjsclear.deobfuscator.Deobfuscator', return_value=nested) as constructor_mock,
        ):
            result = outer.execute()

        constructor_mock.assert_called_once_with('var x = 1;', max_iterations=50, time_budget_seconds=1.5)
        assert result == 'const x = 1;'
