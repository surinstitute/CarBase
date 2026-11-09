export const safetySections = [
  {
    title: "Alertas de colisión",
    key: "collisionWarnings",
    fields: [
      {
        key: "fcw",
        label: "Alerta de colisión frontal (Forward Collision Warning, FCW)",
      },
      {
        key: "ldw",
        label: "Alerta de salida de carril (Lane Departure Warning, LDW)",
      },
      {
        key: "bsw",
        label: "Alerta de punto ciego (Blind Spot Warning, BSW)",
      },
      {
        key: "rctw",
        label:
          "Alerta de tráfico cruzado trasero (Rear Cross-Traffic Warning, RCTW)",
      },
    ],
  },
  {
    title: "Intervención de colisión",
    key: "collisionIntervention",
    fields: [
      {
        key: "aebCity",
        label: "Frenado automático en ciudad (City Automatic Emergency Braking)",
      },
      {
        key: "aebPedestrian",
        label:
          "Frenado automático para peatones (Pedestrian Automatic Emergency Braking)",
      },
      {
        key: "aebHighway",
        label:
          "Frenado automático en carretera (Highway Automatic Emergency Braking)",
      },
      {
        key: "aebRear",
        label:
          "Frenado automático trasero (Rear Automatic Emergency Braking)",
      },
    ],
  },
  {
    title: "Asistencia a la conducción",
    key: "drivingControlAssistance",
    fields: [
      {
        key: "lka",
        label: "Mantenimiento de carril (Lane Keeping Assist, LKA)",
      },
      {
        key: "lca",
        label: "Centrado de carril (Lane Centering Assist, LCA)",
      },
      {
        key: "acc",
        label: "Crucero adaptativo (Adaptive Cruise Control, ACC)",
      },
      {
        key: "activeDrivingAssistanceDirectDriverMonitoring",
        label: "Supervisión directa del conductor (Direct Driver Monitoring)",
      },
    ],
  },
  {
    title: "Seguridad trasera",
    key: "rearSeatSafety",
    fields: [
      {
        key: "childSafety",
        label: "Seguridad infantil en plazas traseras (Rear-Seat Child Safety)",
      },
      {
        key: "rearOccupantAlertEndOfTripReminder",
        label:
          "Alerta de ocupante trasero y recordatorio de fin de viaje (Rear Occupant Alert)",
      },
    ],
  },
  {
    title: "Visibilidad y control",
    key: "visibilityAndControl",
    fields: [
      {
        key: "drl",
        label: "Luces diurnas (Daytime Running Lights, DRL)",
      },
      {
        key: "rearViewCamera",
        label: "Cámara de visión trasera (Rear-View Camera)",
      },
      {
        key: "esc",
        label: "Control electrónico de estabilidad (Electronic Stability Control, ESC)",
      },
      {
        key: "tractionControl",
        label: "Control de tracción (Traction Control)",
      },
      {
        key: "abs",
        label: "Frenos antibloqueo (Anti-lock Braking System, ABS)",
      },
    ],
  },
  {
    title: "Airbags y cinturones",
    key: "restraints",
    fields: [
      {
        key: "airbagSideFront",
        label: "Airbags laterales delanteros (Front Side Airbags)",
      },
      {
        key: "airbagSideRear",
        label: "Airbags laterales traseros (Rear Side Airbags)",
      },
      {
        key: "headProtectionAirbag",
        label: "Airbags de cabeza tipo cortina (Head-Protection Airbags)",
      },
      {
        key: "beltPretensioner",
        label: "Pretensor del cinturón (Seat-Belt Pretensioner)",
      },
      {
        key: "beltLoadLimiter",
        label: "Limitador de carga del cinturón (Seat-Belt Load Limiter)",
      },
      {
        key: "kneeAirbag",
        label: "Airbags de rodilla (Knee Airbags)",
      },
    ],
  },
] as const;
