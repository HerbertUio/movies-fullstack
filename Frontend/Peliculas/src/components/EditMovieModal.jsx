// src/components/EditMovieModal.jsx
import React, { useState, useEffect } from 'react';
import axios from '../api/axiosConfig';

function EditMovieModal({ movie, onClose, onMovieUpdated }) {
  const [nombre, setNombre] = useState(movie.nombre);
  const [descripcion, setDescripcion] = useState(movie.descripcion);
  const [duracion, setDuracion] = useState(movie.duracion);
  const [imagen, setImagen] = useState(null);
  const [categoriaId, setCategoriaId] = useState(movie.categoria_id);
  const [categorias, setCategorias] = useState([]);

  useEffect(() => {
    fetchCategorias();
  }, []);

  const fetchCategorias = async () => {
    try {
      const response = await axios.get('/obtenerCategorias');
      setCategorias(response.data);
    } catch (error) {
      console.error('Error al obtener las categorías:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('descripcion', descripcion);
    formData.append('duracion', duracion);
    formData.append('categoria_id', categoriaId);

    if (imagen) {
      formData.append('imagen', imagen);
    }

    try {
      await axios.put(`/actualizarPelicula/${movie.id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onMovieUpdated();
      onClose();
    } catch (error) {
      console.error('Error al actualizar la película:', error);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h2 className="text-2xl font-bold text-white mb-4">Editar Película</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Campo Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-300">Nombre</label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className="mt-1 block w-full px-4 py-2 bg-gray-700 text-white border border-gray-600 rounded-md"
              required
            />
          </div>
          {/* Campo Descripción */}
          <div>
            <label className="block text-sm font-medium text-gray-300">Descripción</label>
            <textarea
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              className="mt-1 block w-full px-4 py-2 bg-gray-700 text-white border border-gray-600 rounded-md"
              required
            ></textarea>
          </div>
          {/* Campo Duración */}
          <div>
            <label className="block text-sm font-medium text-gray-300">Duración (minutos)</label>
            <input
              type="number"
              value={duracion}
              onChange={(e) => setDuracion(e.target.value)}
              className="mt-1 block w-full px-4 py-2 bg-gray-700 text-white border border-gray-600 rounded-md"
              required
            />
          </div>
          {/* Campo Imagen */}
          <div>
            <label className="block text-sm font-medium text-gray-300">Imagen (opcional)</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setImagen(e.target.files[0])}
              className="mt-1 block w-full text-white"
            />
          </div>
          {/* Campo Categoría */}
          <div>
            <label className="block text-sm font-medium text-gray-300">Categoría</label>
            <select
              value={categoriaId}
              onChange={(e) => setCategoriaId(e.target.value)}
              className="mt-1 block w-full px-4 py-2 bg-gray-700 text-white border border-gray-600 rounded-md"
              required
            >
              {categorias.map((categoria) => (
                <option key={categoria.id} value={categoria.id}>
                  {categoria.nombre}
                </option>
              ))}
            </select>
          </div>
          {/* Botones */}
          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-md"
          >
            Actualizar Película
          </button>
          <button
            type="button"
            onClick={onClose}
            className="w-full py-2 px-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-md mt-2"
          >
            Cancelar
          </button>
        </form>
      </div>
    </div>
  );
}

export default EditMovieModal;
