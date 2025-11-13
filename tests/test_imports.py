"""
Pixely Partners - Basic Import Tests

Quick validation that all modules import correctly without syntax errors.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestOrchestrator:
    """Test orchestrator module imports."""

    def test_base_analyzer_import(self):
        """BaseAnalyzer should import without errors."""
        from orchestrator.base_analyzer import BaseAnalyzer
        assert BaseAnalyzer is not None

    def test_analyze_main_import(self):
        """Main analyze.py should import without errors."""
        from orchestrator import analyze
        assert analyze.ANALYSIS_MODULES is not None
        assert len(analyze.ANALYSIS_MODULES) == 10

    def test_all_q_modules_import(self):
        """All Q1-Q10 modules should import without errors."""
        modules_to_import = [
            ("orchestrator.analysis_modules.q1_emociones", "Q1Emociones"),
            ("orchestrator.analysis_modules.q2_personalidad", "Q2Personalidad"),
            ("orchestrator.analysis_modules.q3_topicos", "Q3Topicos"),
            ("orchestrator.analysis_modules.q4_marcos_narrativos", "Q4MarcosNarrativos"),
            ("orchestrator.analysis_modules.q5_influenciadores", "Q5Influenciadores"),
            ("orchestrator.analysis_modules.q6_oportunidades", "Q6Oportunidades"),
            ("orchestrator.analysis_modules.q7_sentimiento_detallado", "Q7SentimientoDetallado"),
            ("orchestrator.analysis_modules.q8_temporal", "Q8Temporal"),
            ("orchestrator.analysis_modules.q9_recomendaciones", "Q9Recomendaciones"),
            ("orchestrator.analysis_modules.q10_resumen_ejecutivo", "Q10ResumenEjecutivo"),
        ]
        for module_name, class_name in modules_to_import:
            module = __import__(module_name, fromlist=[class_name])
            assert hasattr(module, class_name), f"Module {module_name} missing class {class_name}"


class TestFrontend:
    """Test frontend module imports."""

    def test_outputs_dir_import(self):
        """Output directory resolver should import without errors."""
        from frontend.view_components._outputs import get_outputs_dir
        assert get_outputs_dir() is not None
        assert isinstance(get_outputs_dir(), str)

    def test_all_views_import(self):
        """All Q1-Q10 views should import without errors."""
        views_to_import = [
            ("frontend.view_components.qual.q1_view", "display_q1_emociones"),
            ("frontend.view_components.qual.q2_view", "display_q2_personalidad"),
            ("frontend.view_components.qual.q3_view", "display_q3_topicos"),
            ("frontend.view_components.qual.q4_view", "display_q4_marcos_narrativos"),
            ("frontend.view_components.qual.q5_view", "display_q5_influenciadores"),
            ("frontend.view_components.qual.q6_view", "display_q6_oportunidades"),
            ("frontend.view_components.qual.q7_view", "display_q7_sentimiento"),
            ("frontend.view_components.qual.q8_view", "display_q8_temporal"),
            ("frontend.view_components.qual.q9_view", "display_q9_recomendaciones"),
            ("frontend.view_components.qual.q10_view", "display_q10_resumen_ejecutivo"),
        ]
        for module_name, func_name in views_to_import:
            module = __import__(module_name, fromlist=[func_name])
            assert hasattr(module, func_name), f"Module {module_name} missing function {func_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
