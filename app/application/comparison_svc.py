import asyncio
from typing import List, Optional, Tuple

from app.domain.entities import (
    ComparisonVerdict,
    CompetitiveAdvantage,
    Delta,
    EnrichedZone,
)
from app.domain.ports import AnalyticsPort, MLPort

MAX_ZONES = 4


class ComparisonService:
    def __init__(self, analytics_port: AnalyticsPort, ml_port: MLPort):
        self.analytics_port = analytics_port
        self.ml_port = ml_port

    async def compare_zones(
        self,
        dataset_id: str,
        zone_codes: List[str],
        ml_strategy: str,
    ) -> Tuple[List[EnrichedZone], ComparisonVerdict]:

        zone_codes = zone_codes[:MAX_ZONES]

        # ==========================================
        # 1. ORQUESTACIÓN CONCURRENTE (CA 2)
        # ==========================================
        try:
            analytics_data, ml_data = await asyncio.gather(
                self.analytics_port.get_analytics(dataset_id, zone_codes),
                self.ml_port.get_predictions(dataset_id, zone_codes, ml_strategy),
            )
        except Exception as e:
            print(f"🔥 Error crítico en orquestación de red: {e}")
            analytics_data, ml_data = [], []

        if not analytics_data:
            return [], ComparisonVerdict(
                ranking=[],
                winner_code="",
                justification_text="No se encontraron datos analíticos para el dataset proporcionado.",
            )

        if ml_data is None:
            ml_data = []

        # ==========================================
        # 2. MATCHING CON FAULT TOLERANCE POR ZONA (CA 2)
        # ==========================================
        enriched_zones: List[EnrichedZone] = []
        zone_errors: List[dict] = []

        for zone in analytics_data:
            try:
                code = str(zone.get("zone_code") or "")
                if not code:
                    continue

                prediction = next(
                    (m for m in ml_data if isinstance(m, dict) and str(m.get("zone_code")) == code),
                    {},
                )

                enriched_zones.append(
                    EnrichedZone(
                        zone_code=code,
                        zone_name=zone.get("zone_name", f"Zona {code}"),
                        analytics_data={
                            "poblacion":   float(zone.get("poblacion") or 0.0),
                            "ingresos":    float(zone.get("ingresos") or 0.0),
                            "competencia": float(zone.get("competencia") or 0.0),
                        },
                        ml_potential=float(prediction.get("potential_score") or 0.0),
                    )
                )

            except Exception as e:
                zone_errors.append({"zone_code": zone.get("zone_code"), "reason": str(e)})
                print(f"⚠️ Zona {zone.get('zone_code')} falló en el match: {e}")

        if zone_errors:
            print(f"Zonas con error controlado: {zone_errors}")

        if not enriched_zones:
            return [], ComparisonVerdict([], "", "Error al procesar el cruce de información territorial.")

        # ==========================================
        # 3. CÁLCULO DE DELTAS MATEMÁTICOS (CA 4)
        # ==========================================
        max_ingresos  = max((z.analytics_data["ingresos"]  for z in enriched_zones), default=0.0)
        max_poblacion = max((z.analytics_data["poblacion"] for z in enriched_zones), default=0.0)

        for zone in enriched_zones:
            delta_ingresos  = zone.analytics_data["ingresos"]  - max_ingresos
            delta_poblacion = zone.analytics_data["poblacion"] - max_poblacion

            zone.deltas.append(Delta(
                metric_name="ingresos",
                difference=round(abs(delta_ingresos), 4),  # ← fix float sucio
                is_advantage=(delta_ingresos == 0.0 and max_ingresos > 0),
            ))
            zone.deltas.append(Delta(
                metric_name="poblacion",
                difference=round(abs(delta_poblacion), 4),  # ← fix float sucio
                is_advantage=(delta_poblacion == 0.0 and max_poblacion > 0),
            ))

        # ==========================================
        # 4. RANKING Y VEREDICTO (CA 5)
        # ==========================================
        enriched_zones.sort(
            key=lambda z: (z.ml_potential * 0.7) + (z.analytics_data["ingresos"] * 0.3),
            reverse=True,
        )

        winner = enriched_zones[0]

        # CA 4 — Ventaja competitiva principal
        main_advantage: Optional[CompetitiveAdvantage] = None
        if len(enriched_zones) > 1:
            second = enriched_zones[1]
            gaps = [
                ("ingresos",  winner.analytics_data["ingresos"]  - second.analytics_data["ingresos"]),
                ("poblacion", winner.analytics_data["poblacion"] - second.analytics_data["poblacion"]),
            ]
            best_metric, best_gap = max(gaps, key=lambda x: x[1])
            if best_gap > 0:
                main_advantage = CompetitiveAdvantage(
                    metric_name=best_metric,
                    delta_vs_second=round(best_gap, 4),
                )

        ventaja_principal = "su alto potencial predictivo detectado por la IA"
        if winner.analytics_data["ingresos"] == max_ingresos and max_ingresos > 0:
            ventaja_principal = "el equilibrio entre ingresos actuales y potencial futuro"

        verdict = ComparisonVerdict(
            ranking=[z.zone_code for z in enriched_zones],
            winner_code=winner.zone_code,
            justification_text=(
                f"Basado en el análisis de {len(enriched_zones)} zonas, "
                f"el sistema recomienda {winner.zone_name}. "
                f"La decisión se fundamenta en {ventaja_principal}."
            ),
            main_competitive_advantage=main_advantage,
        )

        return enriched_zones, verdict