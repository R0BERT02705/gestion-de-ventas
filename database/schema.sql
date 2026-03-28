-- database/schema.sql
-- SQLite

-- Eliminar tablas si existen (para empezar limpio en desarrollo)
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS productos;

-- Tabla de Usuarios (Vendedores)
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,          -- Nombre de usuario para login
    password TEXT NOT NULL,                  -- Contraseña (en texto plano por ahora, luego hash)
    nombre_completo TEXT NOT NULL,            -- Nombre real del vendedor
    rol TEXT DEFAULT 'vendedor',              -- 'admin' o 'vendedor'
    activo BOOLEAN DEFAULT 1,                  -- Para desactivar vendedores sin borrarlos
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Productos
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,              -- Código de barras o SKU
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio_venta REAL NOT NULL CHECK (precio_venta > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    activo BOOLEAN DEFAULT 1,                  -- Para ocultar productos descontinuados
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para búsquedas rápidas
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_productos_codigo ON productos(codigo);
CREATE INDEX idx_productos_nombre ON productos(nombre);

-- Insertar datos de ejemplo para empezar a probar
-- Contraseña 'admin123' y 'vendedor123' (en texto plano por ahora)
INSERT INTO usuarios (username, password, nombre_completo, rol) VALUES
('admin', 'admin123', 'Administrador Principal', 'admin'),
('vendedor1', 'vendedor123', 'Juan Pérez', 'vendedor'),
('vendedor2', 'vendedor123', 'María García', 'vendedor');

INSERT INTO productos (codigo, nombre, descripcion, precio_venta, stock) VALUES
('P001', 'Laptop Gamer', 'Laptop de alta gama para juegos', 1200.00, 5),
('P002', 'Mouse Inalámbrico', 'Mouse ergonómico con receptor USB', 25.50, 50),
('P003', 'Teclado Mecánico', 'Teclado RGB switches rojos', 85.00, 15),
('P004', 'Monitor 24"', 'Monitor Full HD 75Hz', 180.00, 7);

CREATE TABLE ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folio TEXT UNIQUE NOT NULL,               -- Número de folio único
    usuario_id INTEGER NOT NULL,               -- Vendedor que realizó la venta
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);

-- Tabla de Detalle de Venta (líneas)
CREATE TABLE detalle_venta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario REAL NOT NULL CHECK (precio_unitario > 0),
    subtotal REAL NOT NULL CHECK (subtotal > 0),
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_ventas_folio ON ventas(folio);
CREATE INDEX idx_ventas_fecha ON ventas(fecha);
CREATE INDEX idx_ventas_usuario ON ventas(usuario_id);
CREATE INDEX idx_detalle_venta ON detalle_venta(venta_id);