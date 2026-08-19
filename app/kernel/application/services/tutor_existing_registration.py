from __future__ import annotations

import re
from typing import Any


def _entero_formulario(form: Any, clave: str) -> int | None:
    valor = str(form.get(clave) or "").strip()
    coincidencia = re.search(r"-?\d+", valor)
    return int(coincidencia.group()) if coincidencia else None


def _decimal_formulario(form: Any, clave: str) -> float | None:
    try:
        return float(form.get(clave))
    except (TypeError, ValueError):
        return None


def _booleano_formulario(form: Any, clave: str) -> bool:
    return str(form.get(clave) or "").upper() in {"SI", "TRUE", "1", "ON"}


def actualizar_ficha_alumno(alumno: Any, form: Any) -> None:
    """Aplica los campos de la ficha sin crear credenciales ni tutores."""
    alumno.lugar_nacimiento = form.get("lugar_nacimiento")
    alumno.direccion_domicilio = form.get("direccion_familiar")
    alumno.genero = form.get("genero") or alumno.genero
    alumno.aseguradora = form.get("aseguradora")

    alumno.peso_nacer = _decimal_formulario(form, "peso_nacer")
    alumno.talla_nacer = _decimal_formulario(form, "talla_nacer")
    alumno.embarazo_normal = form.get("tipo_embarazo") == "NORMAL"
    alumno.embarazo_complicaciones = form.get("embarazo_complicaciones")
    alumno.parto_normal = form.get("tipo_parto") == "NORMAL"
    alumno.parto_complicaciones = form.get("parto_complicaciones")

    alumno.enfermedades_previas = form.get("enfermedades_previas")
    alumno.tiene_alergias = _booleano_formulario(form, "tiene_alergias")
    alumno.alergias_detalle = form.get("alergias")
    alumno.medicacion_actual = form.get("medicacion")
    problemas = [str(valor).strip() for valor in form.getlist("problemas_salud") if str(valor).strip()]
    otros = str(form.get("problemas_salud_otros") or "").strip()
    if otros:
        problemas.append(otros)
    alumno.problemas_salud = ", ".join(problemas) or None
    alumno.traumatismos_caidas = form.get("traumatismos")

    alumno.horario_sueno_nocturno = form.get("sueno_nocturno")
    alumno.horario_sueno_diurno = form.get("sueno_diurno")
    alumno.lugar_sueno = form.get("donde_duerme")
    alumno.duerme_con = form.get("con_quien_duerme")
    alumno.co_sleeping_bebe_edad = form.get("co_sleeping")
    alumno.usa_chupete = _booleano_formulario(form, "usa_chupete")
    alumno.postura_sueno = form.get("postura_sueno")
    alumno.se_duerme_como = form.get("como_duerme")
    alumno.pesadillas_frecuencia = form.get("pesadillas")
    alumno.problemas_sueno = form.get("problemas_sueno")
    alumno.respuesta_problemas_sueno = form.get("respuesta_sueno")

    alumno.lactancia_materna_meses = _entero_formulario(form, "lactancia_meses")
    alumno.uso_biberon_desde_meses = _entero_formulario(form, "biberon_desde")
    alumno.problemas_succion_masticacion = form.get("problemas_comer")
    dieta = [str(valor).strip() for valor in form.getlist("dieta_actual") if str(valor).strip()]
    dieta_otros = str(form.get("dieta_otros") or "").strip()
    if dieta_otros:
        dieta.append(dieta_otros)
    alumno.dieta_actual = ", ".join(dieta) or None
    alumno.alimentos_en_pure = form.get("tipo_comida") == "PURE"
    alumno.alimentos_rechaza = form.get("alimentos_rechaza")
    alumno.alimentos_prefiere = form.get("alimentos_prefiere")
    alumno.intolerancias_alimenticias = form.get("intolerancias")
    alumno.transicion_alimentacion_solida = form.get("costo_solidos")

    alumno.edad_control_cabeza_meses = _entero_formulario(form, "edad_cabeza")
    alumno.edad_sentarse_meses = _entero_formulario(form, "edad_sentarse")
    alumno.edad_gatear_meses = _entero_formulario(form, "edad_gatear")
    alumno.edad_levantarse_meses = _entero_formulario(form, "edad_pararse")
    alumno.edad_caminar_meses = _entero_formulario(form, "edad_caminar")
    alumno.edad_balbuceo_meses = _entero_formulario(form, "edad_balbuceo")
    alumno.edad_primeras_palabras_meses = _entero_formulario(form, "edad_palabras")
    alumno.edad_primeros_dientes_meses = _entero_formulario(form, "edad_dientes")
    alumno.sintomas_denticion = form.get("sintomas_dientes")
    alumno.problemas_marcha = form.get("problemas_marcha")

    alumno.quien_atiende = form.get("quien_atiende")
    alumno.familiares_en_casa = form.get("quien_vive_casa")
    alumno.familiar_mas_apego = form.get("familiar_apego")
    alumno.actividades_con_padres = form.get("actividades_padres")
    alumno.sentimientos_mas_expresados = form.get("emociones")
    alumno.llora_habitualmente = _booleano_formulario(form, "llora_mucho")
    alumno.circunstancias_llanto = form.get("motivo_llanto")
    alumno.objeto_afectivo = form.get("objeto_apego")
    alumno.con_quien_juega = form.get("con_quien_juega")
    alumno.relacion_con_desconocidos = form.get("relacion_extraños") or form.get("relacion_extranos")

    alumno.contacto_emergencia_nombre = form.get("emergencia_nombre")
    alumno.familiares_autorizados_recogo = form.get("autorizados_recoger")


def actualizar_perfil_tutor_existente(tutor: Any, form: Any) -> None:
    """Actualiza datos declarativos del tutor, manteniendo intacta su cuenta."""
    # La identidad y las credenciales ya fueron verificadas al crear la cuenta.
    # Esta ficha solo completa datos de contacto/laborales reutilizables.
    tutor.ci_numero = str(form.get("tutor1_ci") or tutor.ci_numero).strip()
    tutor.ci_expedido = form.get("tutor1_expedido") or tutor.ci_expedido
    tutor.profesion = form.get("tutor1_profesion") or tutor.profesion
    tutor.lugar_trabajo = form.get("tutor1_lugar_trabajo") or tutor.lugar_trabajo
    tutor.direccion_trabajo = form.get("tutor1_direccion") or tutor.direccion_trabajo
    tutor.celular = str(form.get("tutor1_celular") or tutor.celular).strip()
    tutor.email = form.get("tutor1_email") or tutor.email
