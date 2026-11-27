(() => {
  const link = document.querySelector('#catalogue-destination');
  if (!link) return;
  const target = new URL(link.href);
  const previous = new URL(location.href);
  for (const key of new Set(previous.searchParams.keys())) {
    const name = key === 'tim' ? 'tim_mau' : key;
    if (target.searchParams.has(name) || key === 'nhom') continue;
    for (const value of previous.searchParams.getAll(key)) target.searchParams.append(name, value);
  }
  target.hash = previous.hash;
  location.replace(target.href);
})();
