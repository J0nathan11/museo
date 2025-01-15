from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    #---------------------------------------CLIENTE-------------------------------
    path('agregar-cliente/', views.agregar_cliente, name='agregar_cliente'),

    #----------------------------------VER TALLERES------------------------------
    path('listar-talleres/', views.listar_talleres, name='listar_talleres'),

    path('detalles/<int:id_tall>/', views.detalle_taller, name='detalle_taller'),

    #------------------------------LOGIN ORGANIZADOR--------------------------------------
    path('accounts/login/', views.login_organizador, name='login_organizador'),

    #--------------------------------TALLER ORGANIZADOR--------------------------------------
    path('listar-talleres-organizador/', views.listar_talleres_organizador, name='listar_talleres_organizador'),
    #AGREGAR
    path('agregar-taller/', views.agregar_taller, name='agregar_taller'),
    #ELIMINAR
    path('eliminar-taller/<int:id_tall>/', views.eliminar_taller, name='eliminar_taller'),
    #EDITAR
    path('editar_taller/<int:id_tall>/', views.editar_taller, name='editar_taller'),
    #---------------------------------INSCRIPCION--------------------------------------------------------------------
    path('inscripcion/<int:id_tall>/', views.inscripcion_taller, name='inscripcion_taller'),
    
    # Ruta para consultar la cédula
    path('consultar-inscripcion/', views.consultar_inscripcion, name='consultar_inscripcion'),

    # Ruta para listar las inscripciones de un cliente basado en la cédula
    path('listar-inscripcion/<str:cedula_cli>/', views.listar_inscripcion, name='listar_inscripcion'),
    


]
