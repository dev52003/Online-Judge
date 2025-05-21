n = int(input())
numbers = list(map(int, input().split()))

# The sum of numbers from 1 to n
total_sum = n * (n + 1) // 2

# Subtract the sum of the given numbers to find the missing one
missing_number = total_sum - sum(numbers)

print(missing_number)