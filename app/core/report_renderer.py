from app.models.schemas import ResearchReport


class ReportRenderer:

    def render(self, report: ResearchReport) -> str:

        lines = [
            f"# {report.title}",
            "",
            "## Executive Summary",
            "",
            report.executive_summary,
            "",
            "## Research Question",
            "",
            report.research_question,
            "",
            "## Methodology",
            "",
            report.methodology,
            "",
            "## Key Findings",
            "",
        ]

        for finding in report.key_findings:
            lines.append(
                f"- {finding}"
            )

        lines.extend(
            [
                "",
                "## Evidence & Analysis",
                "",
            ]
        )

        for evidence in report.evidence_analysis:
            lines.append(evidence)
            lines.append("")

        lines.extend(
            [
                "## Limitations",
                "",
            ]
        )

        for limitation in report.limitations:
            lines.append(
                f"- {limitation}"
            )

        lines.extend(
            [
                "",
                "## Conclusion",
                "",
                report.conclusion,
                "",
                "## Sources",
                "",
            ]
        )

        for index, source in enumerate(
            report.sources,
            start=1,
        ):
            lines.append(
                f"{index}. {source}"
            )

        return "\n".join(lines)