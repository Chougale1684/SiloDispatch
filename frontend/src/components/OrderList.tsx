import React from 'react';
   import { Order } from '../api/orders';

   interface OrderListProps {
     orders: Order[];
   }

   const OrderList: React.FC<OrderListProps> = ({ orders }) => (
     <div>
       {orders.map(order => (
         <div key={order.id}>
           <strong>{order.customer_name}</strong> - {order.status}
         </div>
       ))}
     </div>
   );

   export default OrderList;