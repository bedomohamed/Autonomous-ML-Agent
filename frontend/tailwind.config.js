/** @type {import('tailwindcss').Config} */
export default {
    darkMode: ["class"],
    content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
  	extend: {
  		colors: {
  			apple: {
  				blue: '#007AFF',
  				'blue-dark': '#0056CC',
  				gray: {
  					'50': '#FAFAFA',
  					'100': '#F5F5F7',
  					'200': '#E8E8ED',
  					'300': '#D2D2D7',
  					'400': '#86868B',
  					'500': '#6E6E73',
  					'600': '#515154',
  					'700': '#424245',
  					'800': '#1D1D1F',
  					'900': '#000000'
  				},
  				green: '#30D158',
  				red: '#FF3B30',
  				orange: '#FF9500',
  				yellow: '#FFCC00',
  				purple: '#AF52DE'
  			},
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		fontFamily: {
  			sans: [
  				'-apple-system',
  				'BlinkMacSystemFont',
  				'SF Pro Display',
  				'Segoe UI',
  				'Roboto',
  				'Helvetica Neue',
  				'Arial',
  				'sans-serif'
  			]
  		},
  		fontSize: {
  			'title-large': [
  				'34px',
  				{
  					lineHeight: '41px',
  					fontWeight: '700'
  				}
  			],
  			title: [
  				'28px',
  				{
  					lineHeight: '34px',
  					fontWeight: '700'
  				}
  			],
  			'title-2': [
  				'22px',
  				{
  					lineHeight: '28px',
  					fontWeight: '600'
  				}
  			],
  			'title-3': [
  				'20px',
  				{
  					lineHeight: '25px',
  					fontWeight: '600'
  				}
  			],
  			headline: [
  				'17px',
  				{
  					lineHeight: '22px',
  					fontWeight: '600'
  				}
  			],
  			body: [
  				'17px',
  				{
  					lineHeight: '22px',
  					fontWeight: '400'
  				}
  			],
  			callout: [
  				'16px',
  				{
  					lineHeight: '21px',
  					fontWeight: '400'
  				}
  			],
  			subhead: [
  				'15px',
  				{
  					lineHeight: '20px',
  					fontWeight: '400'
  				}
  			],
  			footnote: [
  				'13px',
  				{
  					lineHeight: '18px',
  					fontWeight: '400'
  				}
  			],
  			caption: [
  				'12px',
  				{
  					lineHeight: '16px',
  					fontWeight: '400'
  				}
  			]
  		},
  		borderRadius: {
  			apple: '10px',
  			'apple-lg': '16px',
  			'apple-xl': '20px',
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		boxShadow: {
  			apple: '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
  			'apple-lg': '0 4px 6px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.06)',
  			'apple-xl': '0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)'
  		},
  		animation: {
  			'fade-in': 'fadeIn 0.3s ease-in-out',
  			'slide-up': 'slideUp 0.3s ease-out',
  			'scale-in': 'scaleIn 0.2s ease-out'
  		},
  		keyframes: {
  			fadeIn: {
  				'0%': {
  					opacity: '0'
  				},
  				'100%': {
  					opacity: '1'
  				}
  			},
  			slideUp: {
  				'0%': {
  					transform: 'translateY(10px)',
  					opacity: '0'
  				},
  				'100%': {
  					transform: 'translateY(0)',
  					opacity: '1'
  				}
  			},
  			scaleIn: {
  				'0%': {
  					transform: 'scale(0.95)',
  					opacity: '0'
  				},
  				'100%': {
  					transform: 'scale(1)',
  					opacity: '1'
  				}
  			}
  		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
}