from rest_framework import serializers
from .models import Product, Customer, Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity']

    def validate(self, data):
        product = data['product']
        quantity = data['quantity']
        if quantity > product.stock:
            raise serializers.ValidationError(f"There is not enough in stock for product {product.name}. Stock left: {product.stock}")
        return data


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source='customer', write_only=True
    )
    items = OrderItemSerializer(many=True)

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'reference', 'customer', 'customer_id', 'created_at', 'updated_at', 'items', 'total_price']

    def get_total_price(self, object):
        return object.total_price

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            order_item = OrderItem.objects.create(order=order, **item_data)
            product = order_item.product
            product.stock -= order_item.quantity
            product.save()

        return order
