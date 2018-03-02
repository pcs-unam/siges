# coding: utf-8
from django.conf import settings

solicitud = {
    "registrar_catedra":
    settings.APP_PREFIX + "inicio/solicitudes/%s/registrar-catedra",

    "solicitar_apoyo_económico":
    settings.APP_PREFIX + "inicio/solicitudes/%s",
    "solicitar_baja_tutor":
    settings.APP_PREFIX + "inicio/solicitudes/%s",
    "avisar_ausencia":
    settings.APP_PREFIX + "inicio/solicitudes/%s",

    "registrar_actividad_complementaria":
    settings.APP_PREFIX + "inicio/solicitudes/%s",

    "solicitar_candidatura":
    settings.APP_PREFIX + "inicio/solicitudes/%s",

    "cambiar_comite_tutoral":
    settings.APP_PREFIX + "inicio/solicitudes/%s/elegir-comite-tutoral",

    "seleccionar_jurado_candidatura":
    settings.APP_PREFIX + "inicio/solicitudes/%s/elegir-jurado-candidatura",

    "seleccionar_jurado_grado":
    settings.APP_PREFIX + "inicio/solicitudes/%s/elegir-jurado-grado",

    "cambio_proyecto":
    settings.APP_PREFIX + "inicio/solicitudes/%s/cambiar-proyecto",

    "reportar_suspension":
        settings.APP_PREFIX + "inicio/solicitudes/%s",
}
