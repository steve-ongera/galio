// Add this to your base.html or separate JS file

class SearchAutocomplete {
    constructor() {
        this.searchInput = document.querySelector('#search-input');
        this.searchForm = document.querySelector('#search-form');
        this.autocompleteContainer = null;
        this.currentFocus = -1;
        this.searchTimeout = null;
        
        this.init();
    }
    
    init() {
        if (!this.searchInput) return;
        
        // Create autocomplete container
        this.createAutocompleteContainer();
        
        // Bind events
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.searchInput.addEventListener('focus', (e) => this.handleFocus(e));
        
        // Close autocomplete when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.autocompleteContainer.contains(e.target)) {
                this.hideAutocomplete();
            }
        });
        
        // Handle form submission
        if (this.searchForm) {
            this.searchForm.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }
    
    createAutocompleteContainer() {
        this.autocompleteContainer = document.createElement('div');
        this.autocompleteContainer.className = 'search-autocomplete';
        this.autocompleteContainer.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            max-height: 400px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        
        // Make search input container relative
        const inputContainer = this.searchInput.parentElement;
        inputContainer.style.position = 'relative';
        inputContainer.appendChild(this.autocompleteContainer);
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        if (query.length < 2) {
            this.hideAutocomplete();
            return;
        }
        
        // Debounce search requests
        this.searchTimeout = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300);
    }
    
    handleKeydown(e) {
        const items = this.autocompleteContainer.querySelectorAll('.autocomplete-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.currentFocus++;
            if (this.currentFocus >= items.length) this.currentFocus = 0;
            this.updateFocus(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.currentFocus--;
            if (this.currentFocus < 0) this.currentFocus = items.length - 1;
            this.updateFocus(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (this.currentFocus > -1 && items[this.currentFocus]) {
                items[this.currentFocus].click();
            } else {
                this.searchForm.submit();
            }
        } else if (e.key === 'Escape') {
            this.hideAutocomplete();
            this.searchInput.blur();
        }
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= 2) {
            this.fetchSuggestions(query);
        }
    }
    
    handleSubmit(e) {
        const query = this.searchInput.value.trim();
        if (!query) {
            e.preventDefault();
            return;
        }
        
        // Track search analytics if needed
        this.trackSearch(query);
    }
    
    updateFocus(items) {
        items.forEach((item, index) => {
            if (index === this.currentFocus) {
                item.classList.add('autocomplete-active');
            } else {
                item.classList.remove('autocomplete-active');
            }
        });
    }
    
    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/search/autocomplete/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.suggestions && data.suggestions.length > 0) {
                this.renderSuggestions(data.suggestions, query);
                this.showAutocomplete();
            } else {
                this.hideAutocomplete();
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            this.hideAutocomplete();
        }
    }
    
    renderSuggestions(suggestions, query) {
        this.autocompleteContainer.innerHTML = '';
        this.currentFocus = -1;
        
        // Group suggestions by type
        const grouped = {
            products: [],
            categories: [],
            brands: []
        };
        
        suggestions.forEach(suggestion => {
            if (suggestion.type === 'product') {
                grouped.products.push(suggestion);
            } else if (suggestion.type === 'category') {
                grouped.categories.push(suggestion);
            } else if (suggestion.type === 'brand') {
                grouped.brands.push(suggestion);
            }
        });
        
        // Render products first
        if (grouped.products.length > 0) {
            this.renderSectionHeader('Products');
            grouped.products.forEach(product => this.renderProductSuggestion(product, query));
        }
        
        // Render categories
        if (grouped.categories.length > 0) {
            this.renderSectionHeader('Categories');
            grouped.categories.forEach(category => this.renderCategorySuggestion(category, query));
        }
        
        // Render brands
        if (grouped.brands.length > 0) {
            this.renderSectionHeader('Brands');
            grouped.brands.forEach(brand => this.renderBrandSuggestion(brand, query));
        }
        
        // Add "View all results" option
        this.renderViewAllResults(query);
    }
    
    renderSectionHeader(title) {
        const header = document.createElement('div');
        header.className = 'autocomplete-section-header';
        header.textContent = title;
        header.style.cssText = `
            padding: 8px 15px;
            background: #f8f9fa;
            font-weight: bold;
            font-size: 12px;
            color: #666;
            border-bottom: 1px solid #eee;
        `;
        this.autocompleteContainer.appendChild(header);
    }
    
    renderProductSuggestion(product, query) {
        const item = document.createElement('div');
        item.className = 'autocomplete-item product-suggestion';
        item.style.cssText = `
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        
        const highlightedTitle = this.highlightMatch(product.title, query);
        
        item.innerHTML = `
            <div class="product-image" style="width: 40px; height: 40px; flex-shrink: 0;">
                ${product.image ? 
                    `<img src="${product.image}" alt="${product.title}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;">` :
                    `<div style="width: 100%; height: 100%; background: #f0f0f0; border-radius: 4px; display: flex; align-items: center; justify-content: center;"><i class="fa fa-image" style="color: #ccc;"></i></div>`
                }
            </div>
            <div class="product-info" style="flex: 1; min-width: 0;">
                <div class="product-title" style="font-weight: 500; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    ${highlightedTitle}
                </div>
                <div class="product-details" style="font-size: 12px; color: #666;">
                    <span class="product-category">${product.category}</span>
                    <span style="margin: 0 8px;">•</span>
                    <span class="product-price" style="font-weight: bold; color: #007bff;">Ksh ${product.price}</span>
                    ${!product.in_stock ? '<span style="margin: 0 8px;">•</span><span style="color: #dc3545;">Out of Stock</span>' : ''}
                </div>
            </div>
        `;
        
        item.addEventListener('click', () => {
            window.location.href = product.url;
        });
        
        item.addEventListener('mouseenter', () => {
            const items = this.autocompleteContainer.querySelectorAll('.autocomplete-item');
            this.currentFocus = Array.from(items).indexOf(item);
            this.updateFocus(items);
        });
        
        this.autocompleteContainer.appendChild(item);
    }
    
    renderCategorySuggestion(category, query) {
        const item = document.createElement('div');
        item.className = 'autocomplete-item category-suggestion';
        item.style.cssText = `
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        
        const highlightedTitle = this.highlightMatch(category.title, query);
        
        item.innerHTML = `
            <div class="category-icon" style="width: 30px; text-align: center; color: #007bff;">
                <i class="fa fa-folder"></i>
            </div>
            <div class="category-info" style="flex: 1;">
                <div class="category-title" style="font-weight: 500;">
                    ${highlightedTitle}
                </div>
                <div class="category-count" style="font-size: 12px; color: #666;">
                    ${category.count} products
                </div>
            </div>
        `;
        
        item.addEventListener('click', () => {
            window.location.href = category.url;
        });
        
        item.addEventListener('mouseenter', () => {
            const items = this.autocompleteContainer.querySelectorAll('.autocomplete-item');
            this.currentFocus = Array.from(items).indexOf(item);
            this.updateFocus(items);
        });
        
        this.autocompleteContainer.appendChild(item);
    }
    
    renderBrandSuggestion(brand, query) {
        const item = document.createElement('div');
        item.className = 'autocomplete-item brand-suggestion';
        item.style.cssText = `
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        
        const highlightedTitle = this.highlightMatch(brand.title, query);
        
        item.innerHTML = `
            <div class="brand-icon" style="width: 30px; text-align: center; color: #28a745;">
                <i class="fa fa-tag"></i>
            </div>
            <div class="brand-info" style="flex: 1;">
                <div class="brand-title" style="font-weight: 500;">
                    ${highlightedTitle}
                </div>
                <div class="brand-count" style="font-size: 12px; color: #666;">
                    ${brand.count} products
                </div>
            </div>
        `;
        
        item.addEventListener('click', () => {
            window.location.href = brand.url;
        });
        
        item.addEventListener('mouseenter', () => {
            const items = this.autocompleteContainer.querySelectorAll('.autocomplete-item');
            this.currentFocus = Array.from(items).indexOf(item);
            this.updateFocus(items);
        });
        
        this.autocompleteContainer.appendChild(item);
    }
    
    renderViewAllResults(query) {
        const item = document.createElement('div');
        item.className = 'autocomplete-item view-all-results';
        item.style.cssText = `
            padding: 12px 15px;
            background: #f8f9fa;
            cursor: pointer;
            text-align: center;
            font-weight: bold;
            color: #007bff;
            border-top: 2px solid #007bff;
        `;
        
        item.innerHTML = `
            <i class="fa fa-search" style="margin-right: 5px;"></i>
            View all results for "${query}"
        `;
        
        item.addEventListener('click', () => {
            this.searchForm.submit();
        });
        
        item.addEventListener('mouseenter', () => {
            const items = this.autocompleteContainer.querySelectorAll('.autocomplete-item');
            this.currentFocus = Array.from(items).indexOf(item);
            this.updateFocus(items);
        });
        
        this.autocompleteContainer.appendChild(item);
    }
    
    highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong style="background: #fff3cd;">$1</strong>');
    }
    
    showAutocomplete() {
        this.autocompleteContainer.style.display = 'block';
    }
    
    hideAutocomplete() {
        this.autocompleteContainer.style.display = 'none';
        this.currentFocus = -1;
    }
    
    trackSearch(query) {
        // Track search analytics - implement based on your analytics service
        if (typeof gtag !== 'undefined') {
            gtag('event', 'search', {
                search_term: query
            });
        }
        
        // You can also send to your backend for analytics
        fetch('/analytics/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
            },
            body: JSON.stringify({
                query: query,
                timestamp: new Date().toISOString()
            })
        }).catch(error => {
            console.error('Analytics error:', error);
        });
    }
}

// CSS for autocomplete active state
const autocompleteStyles = `
.autocomplete-active {
    background-color: #f8f9fa !important;
}

.search-autocomplete::-webkit-scrollbar {
    width: 6px;
}

.search-autocomplete::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.search-autocomplete::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

.search-autocomplete::-webkit-scrollbar-thumb:hover {
    background: #a1a1a1;
}

@media (max-width: 768px) {
    .search-autocomplete {
        left: -10px !important;
        right: -10px !important;
        border-radius: 0;
        border-left: none;
        border-right: none;
        max-height: 60vh;
    }
    
    .product-suggestion .product-info .product-title {
        font-size: 14px !important;
    }
    
    .product-suggestion .product-details {
        font-size: 11px !important;
    }
}
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = autocompleteStyles;
document.head.appendChild(styleSheet);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new SearchAutocomplete();
});

// Enhanced search with recent searches functionality
class RecentSearches {
    constructor() {
        this.maxRecentSearches = 5;
        this.storageKey = 'recentSearches';
    }
    
    getRecentSearches() {
        try {
            return JSON.parse(localStorage.getItem(this.storageKey) || '[]');
        } catch {
            return [];
        }
    }
    
    addRecentSearch(query) {
        if (!query || query.length < 2) return;
        
        let recent = this.getRecentSearches();
        
        // Remove if already exists
        recent = recent.filter(search => search.toLowerCase() !== query.toLowerCase());
        
        // Add to beginning
        recent.unshift({
            query: query,
            timestamp: Date.now()
        });
        
        // Keep only max number of searches
        recent = recent.slice(0, this.maxRecentSearches);
        
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(recent));
        } catch (error) {
            console.error('Error saving recent search:', error);
        }
    }
    
    clearRecentSearches() {
        try {
            localStorage.removeItem(this.storageKey);
        } catch (error) {
            console.error('Error clearing recent searches:', error);
        }
    }
    
    renderRecentSearches(container, onSearchClick) {
        const recent = this.getRecentSearches();
        
        if (recent.length === 0) return;
        
        const header = document.createElement('div');
        header.className = 'autocomplete-section-header';
        header.style.cssText = `
            padding: 8px 15px;
            background: #f8f9fa;
            font-weight: bold;
            font-size: 12px;
            color: #666;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;
        
        header.innerHTML = `
            <span><i class="fa fa-clock-o" style="margin-right: 5px;"></i>Recent Searches</span>
            <button type="button" class="clear-recent" style="background: none; border: none; color: #007bff; font-size: 11px; cursor: pointer;">Clear</button>
        `;
        
        const clearButton = header.querySelector('.clear-recent');
        clearButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.clearRecentSearches();
            container.innerHTML = '';
        });
        
        container.appendChild(header);
        
        recent.forEach(search => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item recent-search';
            item.style.cssText = `
                padding: 10px 15px;
                border-bottom: 1px solid #eee;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
                color: #666;
            `;
            
            item.innerHTML = `
                <div class="recent-icon" style="width: 20px; text-align: center;">
                    <i class="fa fa-clock-o"></i>
                </div>
                <div class="recent-query" style="flex: 1;">
                    ${search.query}
                </div>
                <div class="recent-time" style="font-size: 11px; color: #999;">
                    ${this.formatTimeAgo(search.timestamp)}
                </div>
            `;
            
            item.addEventListener('click', () => {
                onSearchClick(search.query);
            });
            
            container.appendChild(item);
        });
    }
    
    formatTimeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / (1000 * 60));
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }
}