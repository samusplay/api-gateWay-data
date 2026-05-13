import asyncio
from typing import List, Tuple

from app.domain.entities import ComparisonVerdict, Delta, EnrichedZone
from app.domain.ports import AnalyticsPort, MLPort


class ComparisonService:
    def __init__(self, analytics_port: AnalyticsPort, ml_port: MLPort):
        self.analytics_port = analytics_port
        self.ml_port = ml_port

    async def compare_zones(self, dataset_id: str, zone_codes: List[str], ml_strategy: str) -> Tuple[List[EnrichedZone], ComparisonVerdict]:
        
        # ==========================================
        # 1. ORQUESTACIÓN CONCURRENTE (CA 2)
        # ==========================================
        try:
            # Usamos el dataset_id y zone_codes para pedir la data exacta
            analytics_task = self.analytics_port.get_analytics(dataset_id, zone_codes)
            ml_task = self.ml_port.get_predictions(dataset_id, zone_codes, ml_strategy)
            
            analytics_data, ml_data = await asyncio.gather(analytics_task, ml_task)
        except Exception as e:
            print(f"🔥 Error crítico en orquestación de red: {e}")
            analytics_data, ml_data = [], []

        # VALIDACIÓN 1: ¿Llegó data de analytics?
        if not analytics_data:
            return [], ComparisonVerdict(
                ranking=[], 
                winner_code="", 
                justification_text="No se encontraron datos analíticos para el dataset proporcionado."
            )

        # VALIDACIÓN 2: Evitar nulos en ML
        if ml_data is None:
            ml_data = []

        # ==========================================
        # 2. MATCHING DE DATOS SEGURO (Cruzando Analytics e IA)
        # ==========================================
        enriched_zones = []
        for zone in analytics_data:
            # VALIDACIÓN 3: Asegurar zone_code
            code = str(zone.get("zone_code") or "")
            if not code:
                continue 
            
            # VALIDACIÓN 4: Buscar la predicción de IA correspondiente en el JSON de ML
            prediction = next(
                (m for m in ml_data if isinstance(m, dict) and str(m.get("zone_code")) == code), 
                {}
            )
            
            # VALIDACIÓN 5: Casting defensivo a float (evita errores si llega un null)
            poblacion = float(zone.get("poblacion") or 0.0)
            ingresos = float(zone.get("ingresos") or 0.0)
            competencia = float(zone.get("competencia") or 0.0)
            ml_potential = float(prediction.get("potential_score") or 0.0)

            enriched_zones.append(EnrichedZone(
                zone_code=code,
                zone_name=zone.get("zone_name", f"Zona {code}"),
                analytics_data={
                    "poblacion": poblacion,
                    "ingresos": ingresos,
                    "competencia": competencia
                },
                ml_potential=ml_potential
            ))

        # VALIDACIÓN 6: Si no hay zonas válidas tras el match
        if not enriched_zones:
            return [], ComparisonVerdict([], "", "Error al procesar el cruce de información territorial.")

        # ==========================================
        # 3. CÁLCULO DE DELTAS MATEMÁTICOS (CA 4)
        # ==========================================
        # Buscamos los líderes de cada métrica para comparar
        max_ingresos = max((z.analytics_data["ingresos"] for z in enriched_zones), default=0.0)
        max_poblacion = max((z.analytics_data["poblacion"] for z in enriched_zones), default=0.0)

        for zone in enriched_zones:
            # Calculamos diferencias (Deltas)
            delta_ingresos = zone.analytics_data["ingresos"] - max_ingresos
            delta_poblacion = zone.analytics_data["poblacion"] - max_poblacion
            
            # Marcamos ventajas competitivas
            zone.deltas.append(Delta(
                metric_name="ingresos", 
                difference=abs(delta_ingresos), 
                is_advantage=(delta_ingresos == 0.0 and max_ingresos > 0)
            ))
            zone.deltas.append(Delta(
                metric_name="poblacion", 
                difference=abs(delta_poblacion), 
                is_advantage=(delta_poblacion == 0.0 and max_poblacion > 0)
            ))

        # ==========================================
        # 4. RANKING Y VEREDICTO (CA 5)
        # ==========================================
        # Ordenamos: 70% peso a la IA, 30% a los ingresos reales
        enriched_zones.sort(
            key=lambda z: (z.ml_potential * 0.7) + (z.analytics_data["ingresos"] * 0.3), 
            reverse=True
        )
        
        winner = enriched_zones[0]
        
        # Redacción del veredicto basado en la data real
        ventaja_principal = "su alto potencial predictivo detectado por la IA"
        if winner.analytics_data["ingresos"] == max_ingresos and max_ingresos > 0:
            ventaja_principal = "el equilibrio entre ingresos actuales y potencial futuro"

        verdict = ComparisonVerdict(
            ranking=[z.zone_code for z in enriched_zones],
            winner_code=winner.zone_code,
            justification_text=f"Basado en el análisis de {len(enriched_zones)} zonas, el sistema recomienda {winner.zone_name}. La decisión se fundamenta en {ventaja_principal}."
        )

        return enriched_zones, verdict