def second_largest(numbers):
    if len(numbers) < 2:
        return None  # Not enough numbers to have a second largest
        
    largest = float('-inf')
    second_largest = float('-inf')
    
    for num in numbers:
        if num > largest:
            # Found a new largest, so the old largest becomes the second largest
            second_largest = largest
            largest = num
        elif largest > num > second_largest:
            # Number is smaller than largest, but bigger than current second largest
            second_largest = num
            
    if second_largest == float('-inf'):
        return None  # All numbers in the list were identical (e.g., [5, 5, 5])
        
    return second_largest

print(second_largest([6, 7, 9, 2, 4, 5]))  # Output: 7