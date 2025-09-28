import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  async getHealth() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  async getStations() {
    const response = await apiClient.get('/stations');
    return response.data;
  },

  async getItems() {
    const response = await apiClient.get('/items');
    return response.data;
  },

  async getItem(id) {
    const response = await apiClient.get(`/items/${id}`);
    return response.data;
  },

  async createItem(item) {
    const response = await apiClient.post('/items', item);
    return response.data;
  },

  async createTrip(cardUuid, stationId) {
    const response = await apiClient.post('/trips', {
      card_uuid: cardUuid,
      source_station_id: stationId
    });
    return response.data;
  },

  async getMinimumFare() {
    const response = await apiClient.get('/pricing/minimum');
    return response.data;
  },

  async getFareBetweenStations(stationAId, stationBId) {
    const response = await apiClient.get(`/pricing/between/${stationAId}/${stationBId}`);
    return response.data;
  },

  async getAllPricing() {
    const response = await apiClient.get('/pricing');
    return response.data;
  },

  async createCard(initialBalance, uuid = null) {
    const payload = {
      initial_balance: initialBalance
    };
    if (uuid) {
      payload.uuid = uuid;
    }
    const response = await apiClient.post('/cards', payload);
    return response.data;
  },

  async getCardByUuid(uuid) {
    const response = await apiClient.get(`/cards/uuid/${uuid}`);
    return response.data;
  },

  async addFunds(cardId, amount) {
    const response = await apiClient.post(`/cards/${cardId}/add-funds`, {
      amount: amount
    });
    return response.data;
  },
};

export default apiClient;