<template>
  <div class="charts-container">
    <div class="chart-card">
      <h3>Contacts Added Over Time</h3>
      <Line :data="contactsOverTimeData" :options="lineOptions" />
    </div>
    <div class="chart-card">
      <h3>Transaction Distribution</h3>
      <Bar :data="transactionData" :options="barOptions" />
    </div>
    <div class="chart-card">
      <h3>Contact Tags Distribution</h3>
      <Pie :data="tagDistributionData" :options="pieOptions" />
    </div>
  </div>
</template>

<script>
import { Line, Bar, Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
  BarElement,
  ArcElement
} from 'chart.js'
import { wsManager } from '../services/api'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
  BarElement,
  ArcElement
)

export default {
  name: 'ContactCharts',
  components: { Line, Bar, Pie },
  props: {
    contacts: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      lineOptions: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 500
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        },
        plugins: {
          legend: {
            labels: {
              color: '#2c3e50'
            }
          }
        }
      },
      barOptions: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 500
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        },
        plugins: {
          legend: {
            labels: {
              color: '#2c3e50'
            }
          }
        }
      },
      pieOptions: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 500
        },
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: '#2c3e50'
            }
          }
        }
      },
      chartData: null,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        },
        animation: {
          duration: 500
        }
      },
      wsUnsubscribe: null
    }
  },
  computed: {
    contactsOverTimeData() {
      if (!Array.isArray(this.contacts)) return { labels: [], datasets: [] };
      
      const sortedContacts = [...this.contacts].sort((a, b) => a.id - b.id)
      const labels = sortedContacts.map((_, index) => `Contact ${index + 1}`)
      
      return {
        labels,
        datasets: [{
          label: 'Total Contacts',
          data: sortedContacts.map((_, index) => index + 1),
          borderColor: 'rgba(33, 147, 176, 0.8)',
          backgroundColor: 'rgba(33, 147, 176, 0.2)',
          tension: 0.4,
          fill: true
        }]
      }
    },
    transactionData() {
      if (!Array.isArray(this.contacts)) return { labels: [], datasets: [] };
      
      const amounts = this.contacts.map(c => c.lastTransaction)
      const labels = this.contacts.map(c => c.name)
      
      return {
        labels,
        datasets: [{
          label: 'Last Transaction Amount',
          data: amounts,
          backgroundColor: amounts.map(amount => 
            amount > 0 ? 'rgba(46, 204, 113, 0.3)' : 'rgba(231, 76, 60, 0.3)'
          ),
          borderColor: amounts.map(amount => 
            amount > 0 ? 'rgba(46, 204, 113, 0.8)' : 'rgba(231, 76, 60, 0.8)'
          ),
          borderWidth: 2
        }]
      }
    },
    tagDistributionData() {
      if (!Array.isArray(this.contacts)) return { labels: [], datasets: [] };
      
      const tagCounts = {}
      this.contacts.forEach(contact => {
        tagCounts[contact.tag] = (tagCounts[contact.tag] || 0) + 1
      })
      
      return {
        labels: Object.keys(tagCounts),
        datasets: [{
          data: Object.values(tagCounts),
          backgroundColor: [
            'rgba(52, 152, 219, 0.3)',
            'rgba(155, 89, 182, 0.3)',
            'rgba(52, 73, 94, 0.3)',
            'rgba(46, 204, 113, 0.3)',
            'rgba(230, 126, 34, 0.3)',
            'rgba(231, 76, 60, 0.3)'
          ],
          borderColor: [
            'rgba(52, 152, 219, 0.8)',
            'rgba(155, 89, 182, 0.8)',
            'rgba(52, 73, 94, 0.8)',
            'rgba(46, 204, 113, 0.8)',
            'rgba(230, 126, 34, 0.8)',
            'rgba(231, 76, 60, 0.8)'
          ],
          borderWidth: 2
        }]
      }
    }
  },
  methods: {
    updateChart() {
      // Ensure contacts is an array
      if (!Array.isArray(this.contacts)) {
        this.chartData = {
          labels: [],
          datasets: [{
            label: 'Last Transaction Amount',
            backgroundColor: [],
            borderColor: [],
            borderWidth: 1,
            data: []
          }]
        };
        return;
      }
      
      const transactions = this.contacts.map(c => c.lastTransaction);
      const labels = this.contacts.map(c => c.name);
      
      this.chartData = {
        labels,
        datasets: [
          {
            label: 'Last Transaction Amount',
            backgroundColor: transactions.map(t => 
              t > 0 ? 'rgba(75, 192, 192, 0.2)' : 'rgba(255, 99, 132, 0.2)'
            ),
            borderColor: transactions.map(t => 
              t > 0 ? 'rgb(75, 192, 192)' : 'rgb(255, 99, 132)'
            ),
            borderWidth: 1,
            data: transactions
          }
        ]
      };
    }
  },
  watch: {
    contacts: {
      handler() {
        this.updateChart();
      },
      deep: true,
      immediate: true
    }
  },
  mounted() {
    // Listen for WebSocket updates
    this.wsUnsubscribe = wsManager.addListener(data => {
      if (['new_contact', 'update_contact', 'delete_contact', 'new_transaction'].includes(data.type)) {
        this.updateChart();
      }
    });
  },
  beforeUnmount() {
    if (this.wsUnsubscribe) {
      this.wsUnsubscribe();
    }
  }
}
</script>

<style scoped>
.charts-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
  margin: 20px 0;
  padding: 20px;
}

@media (min-width: 768px) {
  .charts-container {
    grid-template-columns: repeat(3, 1fr);
  }
}

.chart-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  height: 400px;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin: 0 0 15px 0;
  color: #ffffff;
  text-align: center;
  font-weight: 500;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-card > div {
  flex: 1;
  position: relative;
}

/* Add this to ensure the chart takes remaining space */
.chart-card:nth-child(3) {
  height: 380px;
}

/* Make sure the canvas has proper dimensions */
.chart-card > * {
  flex: 1;
  width: 100%;
  position: relative;
}
</style> 