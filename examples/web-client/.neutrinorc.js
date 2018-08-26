module.exports = {
    use: [
        '@neutrinojs/standardjs',

        ['@neutrinojs/react', {
            devServer: {
                host: '127.0.0.1',
                port: 8000,
                https: false,
            },
            html: {
                title: 'web-client'
            }
        }],

        '@neutrinojs/jest',

        // Use absolute paths or it will break on nested pages...
        (neutrino)=> {
            neutrino.config.output.publicPath("/");
        },

        ['@neutrinojs/style-loader', {
            test: /\.global\.(css|sass|scss)$/,
            modulesTest: /(?<!\.global)\.(css|sass|scss)$/,
            modules: true,
            css: {
                localIdentName: '[local]--[hash:base64:8]',
            },
            loaders: [
                {
                    loader: 'sass-loader',
                    useId: 'sass',
                    options: {
                        includePaths: ['node_modules', 'src'],
                        localIdentName: '[local]--[hash:base64:8]',
                    }
                },
                {
                    loader: 'postcss-loader',
                    options: {
                        plugins: [
                            require('autoprefixer')({
                                browsers: [
                                    '>1%',
                                    'last 4 versions',
                                    'Firefox ESR',
                                    'not ie < 9', // React doesn't support IE8 anyway
                                ],
                                flexbox: 'no-2009',
                            }),
                        ]
                    }
                }
            ]
        }],

        (neutrino) => {
            neutrino.config.resolve
                    .modules
                    .add(neutrino.options.source);
        },

        ['@neutrinojs/eslint', {
            eslint: {
                plugins: ['import', 'flowtype', 'jsx-a11y', 'react'],
                rules: {
                    semi: ['error', 'always'],
                },
                baseConfig: {extends: ['eslint-config-react-app']},
            }
        }],

    ]
};
