from django.urls import path
from . import views

urlpatterns = [
    path("", views.inventario, name='inventario'),
    path('categoria/<id>/', views.view_categorias, name='view_categoria'),
    path("stock/", views.main_stock, name='inventario_general'),
    path("agregarProductos/", views.addProducts, name='addProducto'),
    path('update/<id>/', views.updateProduct, name='uptProduct'),
    path('delete/<id>/', views.eliminarProducto, name='dltProduct'),

    #Reportes
    path('reporteStock/', views.reporte_stock.as_view(), name="pdf_stock"),
    path('export/', views.export_stock_to_excel, name='excel_stock'),
    path('reporte/pdf/<int:id>/', views.generar_reporte_pdf.as_view(), name='reporte_pdf'),
    path('reporte/excel/<int:id>/', views.generar_reporte_excel, name='reporte_excel'),
    path('agregarCategoria/', views.agregarCategoria, name='add_categoria'),
    path('updateCategoria/<id>/', views.updateCategoria, name='uptCategoria'),
    path('deleteCategoria/<id>/', views.eliminarCategoria, name='dltCategoria'),
    
    path('producto/<int:producto_id>/transacciones/', views.producto_transacciones, name='producto_transacciones'),
    path('reporte_transacciones/<int:producto_id>/', views.ReporteTransacciones.as_view(), name='reporte_transacciones_pdf'),
    path("agregarUnidad/", views.agregarUnidad, name='addUnidad'),
    path('actualizarUnidad/<int:id>/', views.updateUnidad, name='updateUnidad'),
    path('eliminarUnidad/<int:id>/', views.eliminarUnidad, name='deleteUnidad'),

    path('bodegas/', views.bodegas, name='bodegas'),
    path('bodegas/verBodega/<int:id>/', views.verBodegas, name='verBodega'),
    path('bodegas/agregar/', views.agregar_bodega, name='agregar_bodega'),
    path('bodegas/actualizar/<int:id>/', views.actualizar_bodega, name='actualizar_bodega'),
    path('bodegas/eliminar/<int:id>/', views.eliminar_bodega, name='eliminar_bodega'),

    # Rutas para Subcategorías
    path('subcategorias/', views.listar_subcategorias, name='listar_subcategorias'),
    path('subcategorias/agregar/', views.agregar_subcategoria, name='agregar_subcategoria'),
    path('subcategorias/actualizar/<int:id>/', views.actualizar_subcategoria, name='actualizar_subcategoria'),
    path('subcategorias/eliminar/<int:id>/', views.eliminar_subcategoria, name='eliminar_subcategoria'),

    # Rutas para Precios por Unidad
    path('precios/unidad/', views.agregar_precio_por_unidad, name='addPrecioPorUnidad'),
    path('precios/unidad/actualizar/<int:id>/', views.actualizar_precio_por_unidad, name='actualizar_precio_por_unidad'),
    path('precios/unidad/eliminar/<int:id>/', views.eliminar_precio_por_unidad, name='eliminar_precio_por_unidad'),

    # Rutas para Historial de Precios
    path('historial/precio/', views.agregar_historial_precio, name='addHistorialPrecio'),
    path('historial/precio/actualizar/<int:id>/', views.actualizar_historial_precio, name='actualizar_historial_precio'),
    path('historial/precio/eliminar/<int:id>/', views.eliminar_historial_precio, name='eliminar_historial_precio'),

    # Rutas para Variaciones de Producto
    path('variaciones/producto/', views.agregar_variacion_producto, name='addVariacionProducto'),
    path('variaciones/producto/actualizar/<int:id>/', views.actualizar_variacion_producto, name='actualizar_variacion_producto'),
    path('variaciones/producto/eliminar/<int:id>/', views.eliminar_variacion_producto, name='eliminar_variacion_producto'),

    # Rutas para Stock en Bodega
    path('bodega/crear/', views.agregar_stock_bodega, name='addStockBodega'),
    path('bodega/actualizar/<int:id>/', views.actualizar_stock_bodega, name='actualizar_stock_bodega'),

]