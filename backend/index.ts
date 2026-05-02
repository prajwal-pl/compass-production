import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

import authRoutes from './routes/auth';
import serviceRoutes from './routes/services';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.send('Hello, World!');
});

app.use('/api/auth', authRoutes);
app.use('/api/service', serviceRoutes);

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});