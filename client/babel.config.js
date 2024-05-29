// babel.config.js
module.exports = {
        presets: [
            '@babel/preset-env',
            '@babel/preset-react', // This line is added
        ],
        plugins: [
            '@babel/plugin-proposal-class-properties',
        ],
}